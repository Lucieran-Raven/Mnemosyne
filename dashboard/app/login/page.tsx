"use client";

import { SignIn } from "@clerk/nextjs";

export default function LoginPage() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-background to-muted relative">
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[400px]">
        <SignIn 
          routing="hash"
          redirectUrl="/dashboard"
          appearance={{
            elements: {
              rootBox: "w-full",
              card: "bg-card border border-border shadow-lg",
            }
          }}
        />
      </div>
    </div>
  );
}
