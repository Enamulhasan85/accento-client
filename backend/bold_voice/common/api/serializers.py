from collections import OrderedDict
from typing import Generator, Mapping, Tuple, Type, TypeVar

from django.core.exceptions import FieldDoesNotExist, ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Model
from django.db.models.fields.related import ForeignObject
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field, SkipField, empty, get_error_detail
from rest_framework.serializers import ListSerializer, ModelSerializer
from rest_framework.settings import api_settings

ModelType = TypeVar('ModelType', bound=Model)
FieldType = TypeVar('FieldType', bound=Field)

ForwardRelation = Tuple[FieldType, ForeignObject]
ReverseRelation = Tuple[FieldType, ForeignObjectRel]


# noinspection PyMethodMayBeStatic
class NestedModelSerializer(ModelSerializer):
    class Meta:
        model: Type[ModelType]

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls()
        list_serializer_class = getattr(cls.Meta, 'list_serializer_class', ListSerializer)
        return list_serializer_class(*args, **kwargs)

    def _extract_relations(self):
        forward_relations: OrderedDict[str, ForwardRelation] = OrderedDict()
        reverse_relations: OrderedDict[str, ReverseRelation] = OrderedDict()

        fields: Generator[FieldType, None, None] = self._writable_fields
        for field in fields:
            try:
                related_field = self.Meta.model._meta.get_field(field.source)
            except FieldDoesNotExist:
                continue  # Skip non-existent fields

            if not isinstance(related_field, (ForeignObject, ForeignObjectRel)):
                continue  # Skip non-related fields

            direct = isinstance(related_field, ForeignObject)
            relations = forward_relations if direct else reverse_relations
            relations[field.field_name] = (field, related_field)

        return forward_relations, reverse_relations

    def _is_writable_nested_serializer(self, field):
        return (
                field in self._writable_fields and
                isinstance(field, (ModelSerializer, ListSerializer))
        )

    @property
    def _primitive_fields(self):
        for field in self.fields.values():
            if not self._is_writable_nested_serializer(field):
                yield field

    @property
    def _nested_fields(self):
        for field in self.fields.values():
            if self._is_writable_nested_serializer(field):
                yield field

    def initialize_parent_serializer_context(self, relations):
        for field_name, (field, related_field) in relations.items():
            model_class: Type[ModelType] = self.Meta.model
            _key = '%s.%s' % (
                model_class._meta.model_name,
                related_field.name
            )
            if _key not in self.context:
                continue  # related model not in the context; skip it

            field.required = False
            field.default = self.context[_key]

    def get_raw_instance(self, attrs):
        instance: ModelType = self.Meta.model()
        for field in self._primitive_fields:
            # First, check if the field is provided in the data.
            value = attrs.get(field.source, None)

            # If not, check if the field is provided in the context.
            if value is None:
                _key = '%s.%s' % (self.Meta.model._meta.model_name, field.source)
                value = self.context.get(_key, None)

            # Otherwise, get the value from the instance.
            if value is None:
                value = getattr(self.instance, field.source, None)

            setattr(instance, field.source, value)

        return instance

    def configure_nested_serializer_context(self, relations, raw_instance, data):
        for field_name, (field, related_field) in relations.items():
            if field_name not in data:
                continue  # Data not provided; skip it

            model_class: Type[ModelType] = related_field.related_model
            _key = '%s.%s' % (
                model_class._meta.model_name,
                related_field.field.name
            )
            self.context[_key] = raw_instance

            field_instance = getattr(self.instance, field.source, None)
            if hasattr(field_instance, 'all'):
                field_instance = field_instance.all()

            # TODO (sayed): handle partial updates for forward relations

            field.instance = field_instance
            field.initial_data = data[field_name]

    def run_nested_field_validation(self, field, data=empty):
        return field.run_validation(data)

    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        forward_relations, reverse_relations = self._extract_relations()

        # Check if any related fields are provided in the context. If so, we need
        # to set the default value for the fields to avoid validation errors.
        self.initialize_parent_serializer_context(forward_relations)

        # Validate primitive fields
        primitive_value = self._to_internal_value(data, primitive=True)

        # The nested serializer may need access to the parent instance for data
        # validation. To enable this, we pass the parent instance to the context,
        # allowing the nested serializer to reference it during the validation.
        raw_instance = self.get_raw_instance(primitive_value)
        self.configure_nested_serializer_context(reverse_relations, raw_instance, data)

        # Validate nested fields
        nested_value = self._to_internal_value(data, primitive=False)

        default_ordering = {}

        for field in self._writable_fields:
            if field.source in primitive_value:
                default_ordering[field.source] = primitive_value[field.source]
            elif field.source in nested_value:
                default_ordering[field.source] = nested_value[field.source]

        return default_ordering

    def _to_internal_value(self, data, primitive=True):
        ret = {}
        errors = {}
        fields = self._primitive_fields if primitive else self._nested_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = (
                    field.run_validation(primitive_value)
                    if primitive
                    else self.run_nested_field_validation(field, primitive_value)
                )
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                self.set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret

    def save_forward_relations(self, forward_relations, validated_data):
        pass  # TODO (sayed): Implement this method

    def save_reverse_relations(self, reverse_relations, instance, validated_data):
        for field_name, (field, related_field) in reverse_relations.items():
            if field.source not in validated_data:
                continue  # Data not provided; skip it

            field_instance = getattr(instance, field.source, None)
            if hasattr(field_instance, 'all'):
                field_instance = field_instance.all()

            field_data = validated_data[field.source]
            for child_field_data in field_data:
                child_field_data.update({related_field.field.name: instance})

            field.update(field_instance, field_data)

    def collect_nested_validated_data(self, validated_data):
        nested_validate_data = {}

        for field in self._nested_fields:
            field_data = validated_data.pop(field.source, None)
            if field_data is not None:
                nested_validate_data[field.source] = field_data

        return nested_validate_data

    @transaction.atomic
    def save(self, **kwargs):
        return super().save(**kwargs)

    def create(self, validated_data):
        forward_relations, reverse_relations = self._extract_relations()

        nested_validate_data = self.collect_nested_validated_data(validated_data)
        self.save_forward_relations(forward_relations, nested_validate_data)
        instance = super().create(validated_data)
        self.save_reverse_relations(reverse_relations, instance, nested_validate_data)
        return instance

    def update(self, instance, validated_data):
        forward_relations, reverse_relations = self._extract_relations()

        nested_validate_data = self.collect_nested_validated_data(validated_data)
        self.save_forward_relations(forward_relations, nested_validate_data)
        instance = super().update(instance, validated_data)
        self.save_reverse_relations(reverse_relations, instance, nested_validate_data)
        return instance


class NestedListSerializer(ListSerializer):
    default_error_messages = {
        'duplicate': _('Duplicate entries are not allowed.'),
        'does_not_exist': _('Invalid pk "{pk_value}" - object does not exist.'),
    }

    def __init__(self, *args, **kwargs):
        self.delete_excluded = kwargs.pop('delete_excluded', False)
        super().__init__(*args, **kwargs)

    def run_child_validation(self, data):
        # Safely get the id from the request data
        _id = data.get('id', None)

        instance = self.instance or []  # instance can be None (ie: create request)
        child_instance = next((item for item in instance if item.id == _id), None)

        if _id and not child_instance:
            try:
                self.fail('does_not_exist', pk_value=_id)
            except ValidationError as exc:
                raise ValidationError({'id': exc.detail})

        # Store the original value of the partial attribute
        _partial = self.root.partial

        self.root.partial = _partial and _id is not None
        self.child.instance = child_instance
        self.child.initial_data = data

        try:
            ret = super().run_child_validation(data)
        finally:
            # Reset the partial value to the original value
            self.root.partial = _partial

        return ret

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # Run custom validation
        self._validate_unique_entries(attrs)
        return attrs

    def _validate_unique_entries(self, attrs):
        data_ids = [data.get('id') for data in attrs if data.get('id') is not None]
        if len(data_ids) != len(set(data_ids)):
            self.fail('duplicate')  # Duplicate entries are not allowed

    def create(self, validated_data):
        raise NotImplementedError(
            'This method is not implemented because both bulk creation and bulk updates are '
            'handled within the `update` method. To support these operations in a single API, '
            'always pass an instance or an empty queryset, even when creating new entries.'
        )

    def update(self, instance, validated_data):
        instance_mapping = {item.id: item for item in instance}
        ret = []
        for data in validated_data:
            item = instance_mapping.get(data.get('id'), None)
            if item is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(item, data))
                instance_mapping.pop(item.id)

        if self.delete_excluded:
            for item in instance_mapping.values():
                item.delete()

        return ret


class BulkDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
    )
