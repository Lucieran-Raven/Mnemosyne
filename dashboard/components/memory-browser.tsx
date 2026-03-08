"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listMemories, deleteMemory, Memory } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Database, Trash2, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { useState } from "react";

export function MemoryBrowser() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["memories", page],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return listMemories(token, page);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (memoryId: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return deleteMemory(token, memoryId);
    },
    onSuccess: () => {
      toast.success("Memory deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["memories"] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete: ${error.message}`);
    },
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Memory Browser</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Memory Browser</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-destructive mb-4">Failed to load memories</p>
            <Button onClick={() => refetch()} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const memories = data?.memories || [];
  const total = data?.total || 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Memory Browser</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            {total} total memories stored
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        {memories.length === 0 ? (
          <div className="text-center py-12">
            <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No memories stored yet</p>
            <p className="text-sm text-muted-foreground mt-2">
              Start using the API to store memories
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {memories.map((memory: Memory) => (
              <div
                key={memory.memory_id}
                className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="secondary">{memory.memory_type}</Badge>
                      <span className="text-xs text-muted-foreground">
                        Confidence: {Math.round(memory.confidence * 100)}%
                      </span>
                    </div>
                    <p className="text-sm line-clamp-2">{memory.content}</p>
                    {memory.entities.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {memory.entities.map((entity) => (
                          <Badge key={entity} variant="outline" className="text-xs">
                            {entity}
                          </Badge>
                        ))}
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-2">
                      Created: {new Date(memory.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive"
                    onClick={() => deleteMutation.mutate(memory.memory_id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
            
            {total > 20 && (
              <div className="flex justify-center gap-2 mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="text-sm text-muted-foreground py-2">
                  Page {page} of {Math.ceil(total / 20)}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page >= Math.ceil(total / 20)}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
