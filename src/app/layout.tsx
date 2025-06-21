import type { Metadata } from "next";






import "./globals.css";



import { DM_Sans, Inter } from "next/font/google";



import { GeistSans } from "geist/font/sans";
import { ThemeProvider } from "next-themes";



import { cn } from "@/lib/utils";
import { Navbar } from "@/components/navbar/Navbar";





const inter = Inter({
    subsets: ["latin"],
    variable: "--font-inter",
    display: "swap",
    weight: ["400", "500", "600", "700"],
});

const dmSans = DM_Sans({
    subsets: ["latin"],
    variable: "--font-dm-sans",
    weight: ["400", "500", "600", "700"],
    display: "swap",
});

export const metadata: Metadata = {
    title: "Accento - The Best Accent Training Platform",
    description: "Accento is the best platform to train your accent and improve your spoken English.",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={cn(inter.className, dmSans.variable, GeistSans.variable, "bg-background antialiased")}>
                <ThemeProvider attribute="class" defaultTheme="dark">
                    <Navbar />
                    {children}
                </ThemeProvider>
            </body>
        </html>
    );
}
