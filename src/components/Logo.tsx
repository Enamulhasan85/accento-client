import Image from "next/image";

import LogoIcon from "@/assets/icon/logo.webp";

interface Props {
    className?: string;
}

export const Logo = ({ className }: Props) => <Image src={LogoIcon} alt="Proxis Logo" className={className} />;
