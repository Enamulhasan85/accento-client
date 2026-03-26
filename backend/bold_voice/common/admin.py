from django.contrib import admin


class TabularInline(admin.TabularInline):
    exclude = ['created_by', 'modified_by']


class TimestampModelAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'modified_by')

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()
