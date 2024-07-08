import React from 'react';
import Link from 'next/link';

const Home = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to the Next.js + Flask App</h1>
        <Link href="/login" className="text-xl text-blue-500 hover:underline">
          Login
        </Link>
      </div>
    </div>
  );
};

export default Home;
