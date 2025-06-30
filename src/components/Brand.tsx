import { Logo } from "./Logo";

export const Brand = () => {
    return (
        <a href={"/"}>
            <div className="flex items-center gap-[10px] text-orange-400">
                <Logo className="h-5 w-5 rounded-lg 2xl:h-8 2xl:w-8" />
                <span className="text-2xl font-semibold">Accento</span>
            </div>
        </a>
    );
};
