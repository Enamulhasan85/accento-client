/** @type {import("next").NextConfig} */
const nextConfig = {
    images: {
        unoptimized: process.env.VERCEL_ENV !== "production",
        remotePatterns: [
            { protocol: "https", hostname: "staging.bv.proxisprep.com" },
            { protocol: "https", hostname: "api.bv.proxisprep.com" },
            // { protocol: "https", hostname: "sgp1.digitaloceanspaces.com" },
            // {
            //     protocol: "https",
            //     hostname: "blog.oneielts.com",
            //     port: "",
            //     pathname: "/wp-content/uploads/**",
            // },
            // {
            //     protocol: "https",
            //     hostname: "lh3.googleusercontent.com",
            //     port: "",
            //     pathname: "/a/**",
            // },
        ],
    },
};
export default nextConfig;
