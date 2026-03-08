"use client";

import { useUser, useClerk, useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { 
  LayoutDashboard, 
  Database, 
  Search, 
  Settings, 
  CreditCard,
  Activity,
  LogOut,
  Brain,
  ExternalLink,
  Plus
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MemoryBrowser } from "@/components/memory-browser";
import { MemorySearch } from "@/components/memory-search";
import { UsageStats } from "@/components/usage-stats";
import { ApiKeys } from "@/components/api-keys";
import { Skeleton } from "@/components/ui/skeleton";
import { getHealthStatus, listMemories } from "@/lib/api";

export default function DashboardPage() {
  const { user, isLoaded } = useUser();
  const { signOut } = useClerk();
  const { getToken } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState("overview");

  // Fetch real stats from API
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return getHealthStatus(token);
    },
    refetchInterval: 30000, // Refresh every 30s
  });

  const { data: memoriesData, isLoading: memoriesLoading } = useQuery({
    queryKey: ["memory-count"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      const result = await listMemories(token, 1);
      return result;
    },
  });

  useEffect(() => {
    if (isLoaded && !user) {
      router.push("/login");
    }
  }, [user, isLoaded, router]);

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">Mnemosyne</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {user.emailAddresses[0]?.emailAddress}
            </span>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => signOut(() => router.push("/login"))}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-[600px]">
            <TabsTrigger value="overview">
              <LayoutDashboard className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="memories">
              <Database className="h-4 w-4 mr-2" />
              Memories
            </TabsTrigger>
            <TabsTrigger value="search">
              <Search className="h-4 w-4 mr-2" />
              Search
            </TabsTrigger>
            <TabsTrigger value="api">
              <CreditCard className="h-4 w-4 mr-2" />
              API Keys
            </TabsTrigger>
            <TabsTrigger value="settings">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card className="p-6">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Total Memories</span>
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {memoriesLoading ? <Skeleton className="h-8 w-20" /> : memoriesData?.total || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {healthData?.database === "connected" ? "✓ Database connected" : "Database status unknown"}
                </p>
              </Card>
              <Card className="p-6">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">API Status</span>
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {healthLoading ? <Skeleton className="h-8 w-20" /> : (healthData?.status === "healthy" ? "✓" : "⚠")}
                </div>
                <p className="text-xs text-muted-foreground">
                  {healthData?.status === "healthy" ? "All systems operational" : "Check API status"}
                </p>
              </Card>
              <Card className="p-6">
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Vector DB</span>
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {healthLoading ? <Skeleton className="h-8 w-20" /> : (healthData?.vector_db === "connected" ? "✓" : "⚠")}
                </div>
                <p className="text-xs text-muted-foreground">
                  {healthData?.vector_db === "connected" ? "Pinecone ready" : "Vector DB status"}
                </p>
              </Card>
              <Card className="p-6">
                <div className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">Plan</span>
                </div>
                <div className="mt-2 text-3xl font-bold">Free</div>
                <p className="text-xs text-muted-foreground">100K ops/month</p>
              </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Usage Trends</h3>
                <UsageStats />
              </Card>
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                <div className="space-y-2">
                  <Button 
                    className="w-full justify-start" 
                    variant="outline"
                    onClick={() => setActiveTab("memories")}
                  >
                    <Database className="h-4 w-4 mr-2" />
                    Browse All Memories
                  </Button>
                  <Button 
                    className="w-full justify-start" 
                    variant="outline"
                    onClick={() => setActiveTab("search")}
                  >
                    <Search className="h-4 w-4 mr-2" />
                    Test Memory Search
                  </Button>
                  <Button 
                    className="w-full justify-start" 
                    variant="outline"
                    asChild
                  >
                    <Link href="http://localhost:8000/docs" target="_blank">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      View API Documentation
                    </Link>
                  </Button>
                </div>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="memories">
            <MemoryBrowser />
          </TabsContent>

          <TabsContent value="search">
            <MemorySearch />
          </TabsContent>

          <TabsContent value="api">
            <ApiKeys />
          </TabsContent>

          <TabsContent value="settings">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Account Settings</h3>
              <p className="text-muted-foreground">
                Manage your account preferences and data.
              </p>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
