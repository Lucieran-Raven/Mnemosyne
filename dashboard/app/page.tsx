"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { 
  Brain, 
  Terminal, 
  Play, 
  Check, 
  X, 
  Globe, 
  Quote,
  ArrowRight,
  Zap,
  Clock,
  DollarSign,
  Languages,
  ChevronDown,
  Sparkles,
  Code2,
  Database,
  Star,
  Cpu,
  Layers,
  Workflow,
  Rocket,
  MessageCircle,
  Command,
  GitBranch,
  Box,
  Hexagon,
  Circle,
  Triangle,
  Square,
  Diamond,
  Target,
  Eye,
  MousePointer2,
  ExternalLink,
  Lock,
  Server,
  Shield,
  TrendingUp,
  Users,
  FileText,
  Microscope,
  Award
} from "lucide-react";

function NavButton({ href, children, variant = "default" }: { href: string; children: React.ReactNode; variant?: "default" | "ghost" | "outline" }) {
  const router = useRouter();
  return (
    <Button 
      variant={variant} 
      onClick={() => router.push(href)}
      className={variant === "ghost" ? "hover:bg-white/5" : variant === "default" ? "bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 text-white" : ""}
    >
      {children}
    </Button>
  );
}
function TiltCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const mouseXSpring = useSpring(x, { stiffness: 500, damping: 100 });
  const mouseYSpring = useSpring(y, { stiffness: 500, damping: 100 });
  
  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["8deg", "-8deg"]);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-8deg", "8deg"]);
  
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    x.set(xPct);
    y.set(yPct);
  };
  
  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };
  
  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      className={`${className}`}
    >
      <div style={{ transform: "translateZ(50px)", transformStyle: "preserve-3d" }}>
        {children}
      </div>
    </motion.div>
  );
}

// Floating Animation Component
function FloatingElement({ 
  children, 
  delay = 0, 
  duration = 3,
  yOffset = 20
}: { 
  children: React.ReactNode; 
  delay?: number;
  duration?: number;
  yOffset?: number;
}) {
  return (
    <motion.div
      animate={{
        y: [0, -yOffset, 0],
      }}
      transition={{
        duration,
        repeat: Infinity,
        repeatType: "loop",
        ease: "easeInOut",
        delay,
      }}
    >
      {children}
    </motion.div>
  );
}

// Glowing Card Component
function GlowingCard({ 
  children, 
  className = "",
  glowColor = "rgba(139, 92, 246, 0.5)"
}: { 
  children: React.ReactNode; 
  className?: string;
  glowColor?: string;
}) {
  return (
    <div className={`relative group ${className}`}>
      <div 
        className="absolute -inset-0.5 rounded-xl opacity-0 group-hover:opacity-100 transition duration-500 blur-xl"
        style={{ background: `linear-gradient(45deg, ${glowColor}, transparent, ${glowColor})` }}
      />
      <div className="relative">
        {children}
      </div>
    </div>
  );
}

// Particle Effect
function Particles() {
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; size: number; duration: number; delay: number }>>([]);
  
  useEffect(() => {
    const newParticles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 4 + 2,
      duration: Math.random() * 20 + 10,
      delay: Math.random() * 5,
    }));
    setParticles(newParticles);
  }, []);
  
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
            background: `radial-gradient(circle, rgba(139, 92, 246, 0.8), transparent)`,
            boxShadow: `0 0 ${p.size * 2}px rgba(139, 92, 246, 0.6), 0 0 ${p.size * 4}px rgba(217, 70, 239, 0.4)`,
          }}
          animate={{
            y: [0, -100, 0],
            x: [0, Math.random() * 50 - 25, 0],
            opacity: [0, 1, 0],
            scale: [1, 1.5, 0],
          }}
          transition={{
            duration: p.duration,
            repeat: Infinity,
            delay: p.delay,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

// Animated Gradient Background
function AnimatedGradient() {
  return (
    <div className="fixed inset-0 -z-20 overflow-hidden">
      <motion.div
        className="absolute inset-0 opacity-30"
        animate={{
          background: [
            "radial-gradient(circle at 0% 0%, rgba(139, 92, 246, 0.4) 0%, transparent 50%)",
            "radial-gradient(circle at 100% 100%, rgba(217, 70, 239, 0.4) 0%, transparent 50%)",
            "radial-gradient(circle at 0% 100%, rgba(139, 92, 246, 0.4) 0%, transparent 50%)",
            "radial-gradient(circle at 100% 0%, rgba(217, 70, 239, 0.4) 0%, transparent 50%)",
            "radial-gradient(circle at 0% 0%, rgba(139, 92, 246, 0.4) 0%, transparent 50%)",
          ],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMSIgZmlsbD0icmdiYSgxMzksIDkyLCAyNDYsIDAuMSkiLz48L3N2Zz4=')] opacity-20" />
    </div>
  );
}

// Interactive Cursor Effect
function CursorFollower() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);
  
  return (
    <>
      <motion.div
        className="fixed pointer-events-none z-50 mix-blend-screen"
        animate={{
          x: mousePosition.x - 150,
          y: mousePosition.y - 150,
        }}
        transition={{
          type: "spring",
          stiffness: 150,
          damping: 15,
          mass: 0.1,
        }}
      >
        <div className="w-[300px] h-[300px] rounded-full bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 blur-3xl" />
      </motion.div>
      <motion.div
        className="fixed pointer-events-none z-50"
        animate={{
          x: mousePosition.x - 8,
          y: mousePosition.y - 8,
        }}
        transition={{
          type: "spring",
          stiffness: 500,
          damping: 28,
        }}
      >
        <div className="w-4 h-4 rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 border border-white/50 shadow-lg shadow-violet-500/50" />
      </motion.div>
    </>
  );
}

// Magnetic Button Component
function MagneticButton({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    setPosition({ x: x * 0.3, y: y * 0.3 });
  };
  
  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 });
  };
  
  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: "spring", stiffness: 150, damping: 15, mass: 0.1 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// 3D Geometric Shapes Background
function GeometricShapes() {
  const shapes = [
    { Icon: Box, x: 10, y: 20, delay: 0, color: "text-violet-500/30" },
    { Icon: Hexagon, x: 85, y: 15, delay: 0.5, color: "text-fuchsia-500/30" },
    { Icon: Circle, x: 75, y: 70, delay: 1, color: "text-pink-500/30" },
    { Icon: Triangle, x: 20, y: 60, delay: 1.5, color: "text-cyan-500/30" },
    { Icon: Square, x: 90, y: 50, delay: 2, color: "text-emerald-500/30" },
    { Icon: Diamond, x: 5, y: 80, delay: 2.5, color: "text-amber-500/30" },
  ];
  
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
      {shapes.map((shape, i) => (
        <FloatingElement key={i} delay={shape.delay} duration={6} yOffset={30}>
          <motion.div
            className={`absolute ${shape.color}`}
            style={{ left: `${shape.x}%`, top: `${shape.y}%` }}
            animate={{
              rotate: [0, 360],
              scale: [1, 1.2, 1],
            }}
            transition={{
              rotate: { duration: 20, repeat: Infinity, ease: "linear" },
              scale: { duration: 4, repeat: Infinity, ease: "easeInOut" },
            }}
          >
            <shape.Icon className="w-16 h-16" strokeWidth={1} />
          </motion.div>
        </FloatingElement>
      ))}
    </div>
  );
}

// Text Scramble Effect
function ScrambleText({ text, className = "" }: { text: string; className?: string }) {
  const [displayText, setDisplayText] = useState(text);
  const chars = "!<>-_\\/[]{}—=+*^?#________";
  
  const scramble = () => {
    let iteration = 0;
    const interval = setInterval(() => {
      setDisplayText(
        text
          .split("")
          .map((char, index) => {
            if (index < iteration) return text[index];
            return chars[Math.floor(Math.random() * chars.length)];
          })
          .join("")
      );
      
      if (iteration >= text.length) clearInterval(interval);
      iteration += 1 / 3;
    }, 30);
  };
  
  return (
    <motion.span 
      className={className}
      onMouseEnter={scramble}
      whileHover={{ scale: 1.05 }}
    >
      {displayText}
    </motion.span>
  );
}

// Parallax Section
function ParallaxSection({ children, speed = 0.5 }: { children: React.ReactNode; speed?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [offsetY, setOffsetY] = useState(0);
  
  useEffect(() => {
    const handleScroll = () => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const scrolled = window.scrollY;
      setOffsetY((scrolled - rect.top) * speed);
    };
    
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [speed]);
  
  return (
    <div ref={ref} style={{ transform: `translateY(${offsetY}px)` }}>
      {children}
    </div>
  );
}

// Glass Card with Border Animation
function GlassCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`relative group ${className}`}>
      <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-2xl opacity-0 group-hover:opacity-70 transition duration-500 blur group-hover:blur-md" />
      <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-500 via-fuchsia-500 to-pink-500 rounded-2xl opacity-0 group-hover:opacity-100 transition duration-500 animate-spin-slow" style={{ animationDuration: '3s' }} />
      <div className="relative bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500/10 via-transparent to-fuchsia-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <div className="relative z-10">{children}</div>
      </div>
    </div>
  );
}

// Spotlight Effect
function SpotlightCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);
  
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    setPosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };
  
  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden ${className}`}
    >
      <div
        className="pointer-events-none absolute -inset-px transition duration-300"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(139,92,246,0.15), transparent 40%)`,
        }}
      />
      {children}
    </div>
  );
}

// Logo/Brand Component
function BrandLogo({ name, color = "text-gray-400" }: { name: string; color?: string }) {
  return (
    <motion.div 
      className={`text-xl font-bold ${color} opacity-60 hover:opacity-100 transition-opacity cursor-default`}
      whileHover={{ scale: 1.05 }}
    >
      {name}
    </motion.div>
  );
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      {/* Global Effects */}
      <CursorFollower />
      <Particles />
      <AnimatedGradient />
      <GeometricShapes />
      
      {/* Navigation */}
      <nav className="border-b border-white/10 sticky top-0 bg-[#0a0a0f]/80 backdrop-blur-xl z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link href="/" className="flex items-center gap-2 group">
              <motion.div
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.5 }}
              >
                <Brain className="h-8 w-8 text-violet-400" />
              </motion.div>
              <span className="text-xl font-bold bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
                Mnemosyne
              </span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              <Link href="/docs" className="text-gray-400 hover:text-white transition-colors relative group">
                Docs
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-violet-500 group-hover:w-full transition-all duration-300" />
              </Link>
              <Link href="/pricing" className="text-gray-400 hover:text-white transition-colors relative group">
                Pricing
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-violet-500 group-hover:w-full transition-all duration-300" />
              </Link>
              <NavButton href="/login" variant="ghost">Sign In</NavButton>
              <NavButton href="/login">Get Started →</NavButton>
            </div>
            <Link href="/login" className="md:hidden">
              <Button size="sm" className="bg-gradient-to-r from-violet-600 to-fuchsia-600">Sign In</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 overflow-hidden">
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-b from-violet-500/10 via-fuchsia-500/5 to-transparent" />
          <motion.div 
            className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 rounded-full blur-3xl"
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            {/* Backed By Badge */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8"
            >
              <span className="text-sm text-gray-400">Backed by</span>
              <span className="text-sm font-semibold text-white">YC W23</span>
              <span className="text-sm text-gray-400">•</span>
              <span className="text-sm font-semibold text-white">Sequoia</span>
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6"
            >
              <span className="block text-white mb-2">
                AI Agents
              </span>
              <span className="block bg-gradient-to-r from-violet-400 via-fuchsia-400 to-pink-400 bg-clip-text text-transparent">
                Forget.
              </span>
              <span className="block text-4xl md:text-5xl lg:text-6xl mt-4 text-gray-400">
                Mnemosyne <span className="text-violet-400 font-bold">Remembers.</span>
              </span>
            </motion.h1>
            
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-xl md:text-2xl text-gray-400 mb-8 max-w-2xl mx-auto"
            >
              A universal, self-improving AI memory layer for LLM applications, powering personalized AI experiences that cut costs by 90%.
            </motion.p>
            
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Button 
                size="lg" 
                onClick={() => window.location.href = "/login"}
                className="bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 text-white font-bold text-lg px-8 h-14 gap-2 shadow-lg shadow-violet-500/25 hover:shadow-violet-500/50 transition-shadow"
              >
                <Terminal className="h-5 w-5" /> Start Building Free
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                onClick={() => window.location.href = "/docs"}
                className="font-semibold text-lg px-8 h-14 gap-2 border-2 border-white/20 hover:bg-white/5 hover:border-violet-500/50 transition-all"
              >
                <Play className="h-5 w-5" /> Watch Demo
              </Button>
            </motion.div>

            {/* Demo Preview */}
            <motion.div 
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="mt-16"
            >
              <TiltCard className="max-w-3xl mx-auto">
                <GlassCard className="p-0 overflow-hidden">
                  <div className="bg-[#0d1117] p-6 text-left">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="flex gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-red-500" />
                        <div className="w-3 h-3 rounded-full bg-yellow-500" />
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                      </div>
                      <span className="ml-2 text-sm text-gray-500">mnemosyne_demo.py</span>
                    </div>
                    <div className="space-y-4">
                      <div className="flex gap-4">
                        <div className="flex-1 bg-white/5 rounded-lg p-4 border border-white/10">
                          <p className="text-sm text-gray-400 mb-2">User Input</p>
                          <p className="text-white">&quot;I prefer aisle seats when flying. But for long flights, make that a window seat.&quot;</p>
                        </div>
                      </div>
                      <div className="flex justify-center">
                        <motion.div
                          animate={{ y: [0, 5, 0] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                        >
                          <ArrowRight className="h-6 w-6 text-violet-400 rotate-90" />
                        </motion.div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-violet-500/10 rounded-lg p-4 border border-violet-500/30">
                          <p className="text-xs text-violet-400 mb-1">Type: Preference</p>
                          <p className="text-sm text-white">Seat Preference</p>
                          <p className="text-xs text-gray-500 mt-1">Aisle for short flights, window for long</p>
                        </div>
                        <div className="bg-emerald-500/10 rounded-lg p-4 border border-emerald-500/30">
                          <p className="text-xs text-emerald-400 mb-1">Confidence: 98%</p>
                          <p className="text-sm text-white">Travel Context</p>
                          <p className="text-xs text-gray-500 mt-1">Extracted from conversation</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              </TiltCard>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Trust Logos Section */}
      <section className="py-12 border-y border-white/5 bg-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-8"
          >
            <p className="text-sm text-gray-500 uppercase tracking-wider">Used by 500+ developers from</p>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="flex flex-wrap justify-center items-center gap-8 md:gap-16"
          >
            {["YC W23", "Sequoia", "Accel", "A16Z", "Basis Set"].map((brand) => (
              <BrandLogo key={brand} name={brand} />
            ))}
          </motion.div>
        </div>
      </section>

      {/* Case Studies Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-violet-500/5 to-transparent" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <p className="text-sm text-violet-400 mb-4">Our Customers</p>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Voices From the Field</h2>
            <p className="text-xl text-gray-400">Mnemosyne helps developers reduce token costs and enhance agents with AI memory.</p>
          </motion.div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {[
              { 
                company: "Sunflower Sober",
                quote: "How Sunflower Sober Scaled Personalized Recovery Support to 80,000+ Users with Mnemosyne.",
                author: "Koby Conrad",
                role: "CEO, Sunflower Sober",
                metric: "80K+ Users",
                icon: Users
              },
              { 
                company: "OpenNote",
                quote: "How OpenNote Scaled Personalized Visual Learning with Mnemosyne While Reducing Token Costs by 40%",
                author: "Abhi Arya",
                role: "Co-Founder, OpenNote",
                metric: "40% Cost Savings",
                icon: TrendingUp
              }
            ].map((study, i) => (
              <TiltCard key={study.company}>
                <SpotlightCard>
                  <GlassCard className="h-full cursor-pointer group">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
                        <study.icon className="h-5 w-5 text-white" />
                      </div>
                      <span className="text-lg font-semibold">{study.company}</span>
                    </div>
                    <p className="text-gray-300 mb-6 text-lg leading-relaxed">{study.quote}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 font-bold">
                          {study.author[0]}
                        </div>
                        <div>
                          <p className="font-medium text-white">{study.author}</p>
                          <p className="text-sm text-gray-500">{study.role}</p>
                        </div>
                      </div>
                      <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30">
                        {study.metric}
                      </Badge>
                    </div>
                  </GlassCard>
                </SpotlightCard>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* For Developers Section */}
      <section className="py-24 bg-gradient-to-b from-[#0a0a0f] via-violet-950/20 to-[#0a0a0f] relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30 mb-4">For Developers</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">One-Line Install</h2>
            <p className="text-xl text-gray-400">Infinite Recall for Your LLM Apps</p>
          </motion.div>
          
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                className="space-y-6"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shrink-0">
                    <Zap className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Memory Compression Engine</h3>
                    <p className="text-gray-400">Mnemosyne intelligently compresses chat history into highly optimized memory representations, minimizing token usage and latency while preserving context fidelity.</p>
                  </div>
                </div>
                
                <div className="space-y-3">
                  {[
                    "Streams live savings metrics to your console",
                    "Cuts prompt tokens by up to 90%",
                    "Retains essential details from long conversations"
                  ].map((item, i) => (
                    <motion.div 
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: i * 0.1 }}
                      className="flex items-center gap-3"
                    >
                      <Check className="h-5 w-5 text-emerald-400 shrink-0" />
                      <span className="text-gray-300">{item}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
              
              <div className="grid grid-cols-2 gap-4">
                <TiltCard>
                  <GlassCard className="text-center cursor-pointer group">
                    <div className="text-3xl font-bold text-white mb-2 group-hover:text-violet-400 transition-colors">Zero</div>
                    <p className="text-sm text-gray-400">Friction Setup</p>
                    <p className="text-xs text-gray-500 mt-1">pip install mnemosyne</p>
                  </GlassCard>
                </TiltCard>
                <TiltCard>
                  <GlassCard className="text-center cursor-pointer group">
                    <div className="text-3xl font-bold text-white mb-2 group-hover:text-violet-400 transition-colors">10+</div>
                    <p className="text-sm text-gray-400">Languages</p>
                    <p className="text-xs text-gray-500 mt-1">Native SEA support</p>
                  </GlassCard>
                </TiltCard>
              </div>
            </div>
            
            <TiltCard>
              <GlassCard className="p-0 overflow-hidden">
                <div className="bg-[#0d1117] p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-red-500" />
                      <div className="w-3 h-3 rounded-full bg-yellow-500" />
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                    </div>
                    <span className="ml-2 text-sm text-gray-500">example.py</span>
                  </div>
                  <pre className="text-sm font-mono">
                    <code>
                      <span className="text-purple-400">from</span>{" "}
                      <span className="text-cyan-400">mnemosyne</span>{" "}
                      <span className="text-purple-400">import</span>{" "}
                      <span className="text-cyan-400">Memory</span>
                      {"\n\n"}
                      <span className="text-gray-500"># Initialize - one line</span>
                      {"\n"}
                      <span className="text-cyan-400">memory</span>{" "}
                      <span className="text-white">=</span>{" "}
                      <span className="text-cyan-400">Memory</span>
                      <span className="text-white">()</span>
                      {"\n\n"}
                      <span className="text-gray-500"># Store</span>
                      {"\n"}
                      <span className="text-cyan-400">memory</span>
                      <span className="text-white">.</span>
                      <span className="text-yellow-400">store</span>
                      <span className="text-white">(</span>
                      <span className="text-green-400">&quot;I&apos;m vegetarian&quot;</span>
                      <span className="text-white">)</span>
                      {"\n\n"}
                      <span className="text-gray-500"># Recall</span>
                      {"\n"}
                      <span className="text-cyan-400">result</span>{" "}
                      <span className="text-white">=</span>{" "}
                      <span className="text-cyan-400">memory</span>
                      <span className="text-white">.</span>
                      <span className="text-yellow-400">recall</span>
                      <span className="text-white">(</span>
                      <span className="text-green-400">&quot;food prefs&quot;</span>
                      <span className="text-white">)</span>
                      {"\n"}
                      <span className="text-gray-500"># → {'{"preference": "vegetarian"}'}</span>
                    </code>
                  </pre>
                </div>
              </GlassCard>
            </TiltCard>
          </div>
        </div>
      </section>

      {/* For Enterprise Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/30 mb-4">For Enterprise</Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Secure Memory Layer</h2>
            <p className="text-xl text-gray-400">That Cuts LLM Spend and Passes Audits</p>
          </motion.div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: "Zero-Trust Security",
                desc: "SOC 2 & HIPAA compliant with BYOK. Your data stays secure and audit-ready.",
                color: "from-emerald-500 to-green-500"
              },
              {
                icon: Server,
                title: "Deploy Anywhere",
                desc: "Run on Kubernetes, air-gapped servers, or private clouds. Same API, same behavior.",
                color: "from-blue-500 to-cyan-500"
              },
              {
                icon: Eye,
                title: "Traceable by Default",
                desc: "Every memory is timestamped, versioned, and exportable. See exactly what your AI knows.",
                color: "from-violet-500 to-purple-500"
              }
            ].map((feature, i) => (
              <TiltCard key={feature.title}>
                <GlowingCard>
                  <GlassCard className="h-full">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4`}>
                      <feature.icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                    <p className="text-gray-400">{feature.desc}</p>
                  </GlassCard>
                </GlowingCard>
              </TiltCard>
            ))}
          </div>
        </div>
      </section>

      {/* Research Section */}
      <section className="py-24 bg-gradient-to-b from-[#0a0a0f] via-fuchsia-950/10 to-[#0a0a0f]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30 mb-4">Research</Badge>
              <h2 className="text-4xl md:text-5xl font-bold mb-4">Benchmarking Mnemosyne</h2>
              <p className="text-lg text-gray-400 mb-6">
                Mnemosyne outperforms OpenAI memory on accuracy, latency, and token savings—benchmarking 26% higher response quality with 90% fewer tokens.
              </p>
              <div className="flex flex-wrap gap-4">
                <div className="flex items-center gap-2 text-emerald-400">
                  <TrendingUp className="h-5 w-5" />
                  <span className="font-semibold">26% Better Quality</span>
                </div>
                <div className="flex items-center gap-2 text-violet-400">
                  <Zap className="h-5 w-5" />
                  <span className="font-semibold">90% Fewer Tokens</span>
                </div>
              </div>
              <Button 
                variant="outline" 
                onClick={() => window.location.href = "/docs"}
                className="border-violet-500/30 hover:bg-violet-500/10"
              >
                <FileText className="h-4 w-4 mr-2" /> Read Research Paper
              </Button>
            </motion.div>
            
            <TiltCard>
              <GlassCard>
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-violet-500/20 flex items-center justify-center">
                        <Brain className="h-5 w-5 text-violet-400" />
                      </div>
                      <span className="font-semibold">Mnemosyne</span>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-emerald-400">98%</p>
                      <p className="text-xs text-gray-500">Accuracy</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gray-500/20 flex items-center justify-center">
                        <span className="text-gray-400 text-xs">OA</span>
                      </div>
                      <span className="font-semibold text-gray-400">OpenAI Memory</span>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-500">72%</p>
                      <p className="text-xs text-gray-500">Accuracy</p>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 rounded-lg border border-violet-500/30">
                    <p className="text-sm text-gray-300">
                      &quot;Mnemosyne demonstrates superior memory retention across long conversations while maintaining sub-100ms latency.&quot;
                    </p>
                    <p className="text-xs text-gray-500 mt-2">— ECAI 2025 Research</p>
                  </div>
                </div>
              </GlassCard>
            </TiltCard>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-600 via-fuchsia-600 to-pink-600" />
        <motion.div 
          className="absolute inset-0 opacity-30"
          animate={{
            background: [
              "radial-gradient(circle at 20% 50%, rgba(255,255,255,0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 80% 50%, rgba(255,255,255,0.3) 0%, transparent 50%)",
              "radial-gradient(circle at 20% 50%, rgba(255,255,255,0.3) 0%, transparent 50%)",
            ],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        />
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <motion.h2 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-5xl md:text-6xl font-bold text-white mb-6"
          >
            Give your AI a memory and personality.
          </motion.h2>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-xl text-white/80 mb-8"
          >
            Instant memory for LLMs—better, cheaper, personal.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Button 
              size="lg" 
              onClick={() => window.location.href = "/login"}
              className="bg-white text-violet-600 hover:bg-white/90 font-bold text-lg px-10 h-16 gap-2 shadow-2xl hover:shadow-white/20 transition-shadow"
            >
              Get Started Free <ArrowRight className="h-5 w-5 inline" />
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              onClick={() => window.location.href = "/pricing"}
              className="border-2 border-white/30 text-white hover:bg-white/10 font-semibold text-lg px-10 h-16"
            >
              View Pricing
            </Button>
          </motion.div>
          
          <motion.p 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4 }}
            className="mt-8 text-white/50"
          >
            100K operations free. No credit card required.
          </motion.p>
        </div>
      </section>

      {/* Enhanced Footer */}
      <footer className="border-t border-white/10 py-16 bg-[#0a0a0f]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
            <div className="col-span-2">
              <Link href="/" className="flex items-center gap-2 mb-4">
                <Brain className="h-8 w-8 text-violet-400" />
                <span className="text-2xl font-bold text-white">Mnemosyne</span>
              </Link>
              <p className="text-gray-500 mb-4 max-w-sm">
                The memory infrastructure layer for AI agents. Give every AI agent perfect, persistent memory.
              </p>
              <div className="flex gap-4">
                {["GitHub", "Discord", "Twitter"].map((social) => (
                  <Link 
                    key={social}
                    href="#" 
                    className="text-gray-500 hover:text-violet-400 transition-colors"
                  >
                    {social}
                  </Link>
                ))}
              </div>
            </div>
            
            {[
              { 
                title: "Product", 
                links: [
                  { name: "Mem0", href: "/" },
                  { name: "OpenMemory", href: "#" },
                  { name: "Pricing", href: "/pricing" },
                  { name: "Changelog", href: "#" }
                ] 
              },
              { 
                title: "Resources", 
                links: [
                  { name: "Docs", href: "/docs" },
                  { name: "API Reference", href: "/docs" },
                  { name: "Blog", href: "#" },
                  { name: "Research", href: "#" }
                ] 
              },
              { 
                title: "Company", 
                links: [
                  { name: "About", href: "#" },
                  { name: "Careers", href: "#" },
                  { name: "Investors", href: "#" },
                  { name: "Contact", href: "#" }
                ] 
              },
              { 
                title: "Legal", 
                links: [
                  { name: "Privacy", href: "#" },
                  { name: "Terms", href: "#" },
                  { name: "Trust Center", href: "#" },
                  { name: "Status", href: "#" }
                ] 
              }
            ].map((section) => (
              <div key={section.title}>
                <h4 className="font-semibold mb-4 text-white">{section.title}</h4>
                <ul className="space-y-2 text-sm text-gray-500">
                  {section.links.map((link) => (
                    <li key={link.name}>
                      <Link 
                        href={link.href} 
                        className="hover:text-violet-400 transition-colors"
                      >
                        {link.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          
          <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-500">
              © 2025 Mnemosyne. Built for Southeast Asia, available worldwide.
            </p>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>Backed by</span>
              <span className="text-white font-semibold">YC W23</span>
              <span>•</span>
              <span className="text-white font-semibold">Sequoia</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
