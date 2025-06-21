"use client";

import * as React from "react";
import Link from "next/link";

import { CircleCheckIcon, CircleHelpIcon, CircleIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger,
    navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

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
    const navMenuItems = [
        {
            label: "Home",
            href: "/",
            description: "Beautifully designed components built with Tailwind CSS.",
        },
        {
            label: "Introduction",
            href: "/docs",
            description: "Re-usable components built using Radix UI and Tailwind CSS.",
        },
        {
            label: "Installation",
            href: "/docs/installation",
            description: "How to install dependencies and structure your app.",
        },
        {
            label: "Typography",
            href: "/docs/primitives/typography",
            description: "Styles for headings, paragraphs, lists...etc",
        },
    ];

    return (
        <nav
            className={cn(
                `border-border-light fixed top-0 z-50 flex h-[64px] items-center border-b bg-white px-8 py-5 2xl:h-[72px]`,
                "w-full justify-center"
            )}
        >
            {/*<Brand />*/}
            {/*<ActionSection />*/}
            <NavigationMenu viewport={false}>
                <NavigationMenuList>
                    {}
                    {/*<NavMenuItem/>*/}
                    <NavigationMenuItem>
                        <NavigationMenuTrigger>Home</NavigationMenuTrigger>
                        <NavigationMenuContent>
                            <ul className="grid gap-2 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]">
                                <li className="row-span-3">
                                    <NavigationMenuLink asChild>
                                        <Link
                                            className="from-muted/50 to-muted flex h-full w-full flex-col justify-end rounded-md bg-linear-to-b p-6 no-underline outline-hidden select-none focus:shadow-md"
                                            href="/"
                                        >
                                            <div className="mt-4 mb-2 text-lg font-medium">shadcn/ui</div>
                                            <p className="text-muted-foreground text-sm leading-tight">
                                                Beautifully designed components built with Tailwind CSS.
                                            </p>
                                        </Link>
                                    </NavigationMenuLink>
                                </li>
                                {/*<ListItem href="/docs" title="Introduction">*/}
                                {/*    Re-usable components built using Radix UI and Tailwind CSS.*/}
                                {/*</ListItem>*/}
                                {/*<ListItem href="/docs/installation" title="Installation">*/}
                                {/*    How to install dependencies and structure your app.*/}
                                {/*</ListItem>*/}
                                {/*<ListItem href="/docs/primitives/typography" title="Typography">*/}
                                {/*    Styles for headings, paragraphs, lists...etc*/}
                                {/*</ListItem>*/}
                            </ul>
                        </NavigationMenuContent>
                    </NavigationMenuItem>
                    <NavigationMenuItem>
                        <NavigationMenuTrigger>Components</NavigationMenuTrigger>
                        <NavigationMenuContent>
                            {/*<ul className="grid w-[400px] gap-2 md:w-[500px] md:grid-cols-2 lg:w-[600px]">*/}
                            {/*    {components.map((component) => (*/}
                            {/*        <ListItem*/}
                            {/*            key={component.title}*/}
                            {/*            title={component.title}*/}
                            {/*            href={component.href}*/}
                            {/*        >*/}
                            {/*            {component.description}*/}
                            {/*        </ListItem>*/}
                            {/*    ))}*/}
                            {/*</ul>*/}
                        </NavigationMenuContent>
                    </NavigationMenuItem>
                    <NavigationMenuItem>
                        <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                            <Link href="/docs">Docs</Link>
                        </NavigationMenuLink>
                    </NavigationMenuItem>
                </NavigationMenuList>
            </NavigationMenu>
        </nav>
    );
}
