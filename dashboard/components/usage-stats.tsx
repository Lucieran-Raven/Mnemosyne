"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { getHealthStatus, listMemories, HealthStatus } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Activity, Database, Server, CheckCircle, XCircle } from "lucide-react";

export function UsageStats() {
  const { getToken } = useAuth();

  const { data: health, isLoading: healthLoading } = useQuery<HealthStatus>({
    queryKey: ["health"],
    queryFn: async () => {
      const token = await getToken();
      return getHealthStatus(token || undefined);
    },
    refetchInterval: 30000,
  });

  const { data: memories, isLoading: memoriesLoading } = useQuery({
    queryKey: ["memory-count"],
    queryFn: async () => {
      const token = await getToken();
      if (!token) return { total: 0 };
      return listMemories(token, 1, 1);
    },
  });

  const isLoading = healthLoading || memoriesLoading;

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </CardContent>
      </Card>
    );
  }

  const services = [
    { name: "API", status: health?.status === "healthy", icon: Server },
    { name: "Database", status: health?.database === "connected", icon: Database },
    { name: "Cache", status: health?.cache === "connected", icon: Activity },
    { name: "Vector DB", status: health?.vector_db === "connected", icon: Database },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Total Memories</span>
              </div>
              <div className="mt-2 text-2xl font-bold">{memories?.total || 0}</div>
            </div>
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">API Version</span>
              </div>
              <div className="mt-2 text-2xl font-bold">{health?.version || "-"}</div>
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h4 className="text-sm font-medium mb-3">Service Health</h4>
            <div className="space-y-2">
              {services.map((service) => (
                <div key={service.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <service.icon className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{service.name}</span>
                  </div>
                  {service.status ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-destructive" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
