"use client";

import * as React from "react";
import Link from "next/link";

import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger,
    navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { Brand } from "@/components/Brand";
import { Logo } from "@/components/Logo";

const components: { title: string; href: string; description: string }[] = [
    {
        title: "Alert Dialog",
        href: "/docs/primitives/alert-dialog",
        description: "A modal dialog that interrupts the user with important content and expects a response.",
    },
    {
        title: "Hover Card",
        href: "/docs/primitives/hover-card",
        description: "For sighted users to preview content available behind a link.",
    },
    {
        title: "Progress",
        href: "/docs/primitives/progress",
        description:
            "Displays an indicator showing the completion progress of a task, typically displayed as a progress bar.",
    },
    {
        title: "Scroll-area",
        href: "/docs/primitives/scroll-area",
        description: "Visually or semantically separates content.",
    },
    {
        title: "Tabs",
        href: "/docs/primitives/tabs",
        description: "A set of layered sections of content—known as tab panels—that are displayed one at a time.",
    },
    {
        title: "Tooltip",
        href: "/docs/primitives/tooltip",
        description:
            "A popup that displays information related to an element when the element receives keyboard focus or the mouse hovers over it.",
    },
];

export function Navbar() {
    return (
        <NavigationMenu viewport={false} className="bg-background border-border max-w-screen border-b">
            <div className="flex h-16 w-full items-center justify-around px-4">
                <Brand />
                <NavigationMenuList>
                    <NavigationMenuItem>
                        <NavigationMenuTrigger>Home</NavigationMenuTrigger>
                        <NavigationMenuContent>
                            <ul className="grid gap-2 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]">
                                <li className="row-span-3">
                                    <NavigationMenuLink asChild>
                                        <Link
                                            className="from-muted/50 to-muted flex h-full w-full flex-col justify-center rounded-md bg-gradient-to-b px-6 py-3 no-underline outline-none select-none focus:shadow-md"
                                            href="/about"
                                        >
                                            <Logo className="h-15 w-15 rounded-lg shadow-md" />
                                            <div className="mb-2 text-lg font-medium text-orange-400">Accento</div>
                                            <p className="text-muted-foreground text-sm leading-tight">
                                                Master your English accent with real-time AI feedback, personalized
                                                lessons, and progress tracking.
                                            </p>
                                        </Link>
                                    </NavigationMenuLink>
                                </li>
                                <ListItem href="/docs" title="What is Accento?">
                                    Learn how Accento helps you practice and improve your English accent with real-time
                                    AI feedback.
                                </ListItem>
                                <ListItem
                                    href="https://play.google.com/store/apps/details?id=com.english.accent_training_app&hl=en"
                                    title="Get on Play Store"
                                >
                                    Download the Accento app from Google Play to start training your accent on Android.
                                </ListItem>
                                <ListItem
                                    href="https://apps.apple.com/us/app/accent-trainer/id6745178009"
                                    title="Get on App Store"
                                >
                                    Access Accento on your iPhone and improve your pronunciation today.
                                </ListItem>
                            </ul>
                        </NavigationMenuContent>
                    </NavigationMenuItem>
                    <NavigationMenuItem>
                        <NavigationMenuTrigger>Components</NavigationMenuTrigger>
                        <NavigationMenuContent>
                            <ul className="grid w-[400px] gap-2 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
                                {components.map((component) => (
                                    <ListItem key={component.title} title={component.title} href={component.href}>
                                        {component.description}
                                    </ListItem>
                                ))}
                            </ul>
                        </NavigationMenuContent>
                    </NavigationMenuItem>
                    <NavigationMenuItem>
                        <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                            <Link href="/docs">Docs</Link>
                        </NavigationMenuLink>
                    </NavigationMenuItem>
                </NavigationMenuList>

                <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                    <Link href="/docs/primitives/alert-dialog">Alert Dialog</Link>
                </NavigationMenuLink>
            </div>
        </NavigationMenu>
    );
}

function ListItem({ title, children, href, ...props }: React.ComponentPropsWithoutRef<"li"> & { href: string }) {
    return (
        <li {...props}>
            <NavigationMenuLink
                asChild
                className="hover:text-primary focus:text-primary data-[state=open]:text-primary transition-colors focus:shadow-md"
            >
                <Link href={href}>
                    <div className="text-sm leading-none font-medium">{title}</div>
                    <p className="text-muted-foreground line-clamp-2 text-sm leading-snug">{children}</p>
                </Link>
            </NavigationMenuLink>
        </li>
    );
}
