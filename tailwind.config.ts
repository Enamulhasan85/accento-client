import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";
import motionPlugin from "tailwindcss-motion";

const config: Config = {
    darkMode: "class",
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/data/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            ...motionPlugin.config?.theme?.extend,
            screens: {
                "1300": "1300px",
                "1440": "1440px",
            },

            fontSize: {
                "geist-h1": [
                    "var(--geist-h1)",
                    {
                        lineHeight: "var(--geist-h1-height)",
                        fontWeight: "var(--geist-h1-weight)",
                    },
                ],
                "geist-h2": [
                    "var(--geist-h2)",
                    {
                        lineHeight: "var(--geist-h2-height)",
                        fontWeight: "var(--geist-h2-weight)",
                    },
                ],
                "geist-h3": [
                    "var(--geist-h3)",
                    {
                        lineHeight: "var(--geist-h3-height)",
                        fontWeight: "var(--geist-h3-weight)",
                    },
                ],
                "geist-h4": [
                    "var(--geist-h4)",
                    {
                        lineHeight: "var(--geist-h4-height)",
                        fontWeight: "var(--geist-h4-weight)",
                    },
                ],
                "geist-h5": [
                    "var(--geist-h5)",
                    {
                        lineHeight: "var(--geist-h5-height)",
                        fontWeight: "var(--geist-h5-weight)",
                    },
                ],
                "geist-h6": [
                    "var(--geist-h6)",
                    {
                        lineHeight: "var(--geist-h6-height)",
                        fontWeight: "var(--geist-h6-weight)",
                    },
                ],
            },

            fontFamily: {
                inter: ["var(--font-inter)", "sans-serif"],
                dmSans: ["var(--font-dm-sans)", "sans-serif"],
                geistSans: ["var(--font-geist-sans)", "sans-serif"],
            },
            colors: {
                white: "hsl(var(--white))",
                background: {
                    DEFAULT: "hsl(var(--background))",
                    secondary: "hsl(var(--background-secondary))",
                },
                foreground: {
                    DEFAULT: "hsl(var(--foreground))",
                    secondary: "hsl(var(--foreground-secondary))",
                    landing: "hsl(var(--foreground-landing))",
                },
                "border-secondary": "hsl(var(--border-secondary))",
                card: {
                    DEFAULT: "hsl(var(--card))",
                    foreground: "hsl(var(--card-foreground))",
                },
                popover: {
                    DEFAULT: "hsl(var(--popover))",
                    foreground: "hsl(var(--popover-foreground))",
                },
                primary: {
                    DEFAULT: "hsl(var(--primary))",
                    foreground: "hsl(var(--primary-foreground))",
                    hover: "hsl(var(--primary-hover))",
                    click: "hsl(var(--primary-click))",
                    shade: "hsl(var(--primary-shade))",
                },
                secondary: {
                    DEFAULT: "hsl(var(--secondary))",
                    foreground: "hsl(var(--secondary-foreground))",
                    shade: "hsl(var(--secondary-shade))",
                    hover: "hsl(var(--secondary-hover))",
                    stroke: "hsl(var(--secondary-stroke))",
                },
                muted: {
                    DEFAULT: "hsl(var(--muted))",
                    foreground: "hsl(var(--muted-foreground))",
                },
                success: {
                    DEFAULT: "hsl(var(--success))",
                    shade: "hsl(var(--success-shade))",
                },
                warn: {
                    DEFAULT: "hsl(var(--warn))",
                    shade: "hsl(var(--warn-shade))",
                },
                accent: {
                    DEFAULT: "hsl(var(--accent))",
                    foreground: "hsl(var(--accent-foreground))",
                },
                destructive: {
                    DEFAULT: "hsl(var(--destructive))",
                    shade: "hsl(var(--destructive-shade))",
                    foreground: "hsl(var(--destructive-foreground))",
                },
                border: "hsl(var(--border))",
                input: "hsl(var(--input))",
                ring: "hsl(var(--ring))",
                chart: {
                    "1": "hsl(var(--chart-1))",
                    "2": "hsl(var(--chart-2))",
                    "3": "hsl(var(--chart-3))",
                    "4": "hsl(var(--chart-4))",
                    "5": "hsl(var(--chart-5))",
                },
            },
            borderRadius: {
                xl: "var(--radius)",
                lg: "calc(var(--radius) - 8px)",
                md: "calc(var(--radius) - 12px)",
                sm: "calc(var(--radius) - 18px)",
            },
            keyframes: {
                "accordion-down": {
                    from: {
                        height: "0",
                    },
                    to: {
                        height: "var(--radix-accordion-content-height)",
                    },
                },
                "accordion-up": {
                    from: {
                        height: "var(--radix-accordion-content-height)",
                    },
                    to: {
                        height: "0",
                    },
                },
                "infinite-scroll": {
                    from: { transform: "translateX(0)" },
                    to: { transform: "translateX(-100%)" },
                },
                "infinite-scroll-reverse": {
                    from: { transform: "translateX(-100%)" },
                    to: { transform: "translateX(0)" },
                },
                progress: {
                    "0%": { transform: "translateX(-100%)" },
                    "100%": { transform: "translateX(100%)" },
                },
            },
            animation: {
                "accordion-down": "accordion-down 0.2s ease-out",
                "accordion-up": "accordion-up 0.2s ease-out",
                "infinite-scroll": "infinite-scroll 80s linear infinite",
                "infinite-scroll-reverse": "infinite-scroll-reverse 80s linear infinite",
                progress: "progress 1.5s ease-in-out infinite",
            },
        },
    },
    plugins: [animate, motionPlugin.handler],
};

export default config;
