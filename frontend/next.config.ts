import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'synapse-videos.s3.ap-south-1.amazonaws.com',
        pathname: '/thumbnails/**',
      },
      {
        protocol: 'https',
        hostname: 'synapse-videos.s3.ap-south-1.amazonaws.com',
        pathname: '/**',
      },
    ],
  },
  reactCompiler: true,
};


module.exports = nextConfig;


export default nextConfig;
