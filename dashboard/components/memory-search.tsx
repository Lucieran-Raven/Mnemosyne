"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useQuery } from "@tanstack/react-query";
import { searchMemories, Memory } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Search, RefreshCw } from "lucide-react";

export function MemorySearch() {
  const { getToken } = useAuth();
  const [query, setQuery] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["memory-search", searchQuery],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      if (!searchQuery) return { memories: [], query: "" };
      return searchMemories(token, searchQuery, 10);
    },
    enabled: !!searchQuery,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(query);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Memory Search</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSearch} className="flex gap-2 mb-6">
          <Input
            placeholder="Search memories..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading}>
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
        </form>

        {isLoading && (
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <p className="text-destructive mb-4">Search failed</p>
            <Button onClick={() => refetch()} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        )}

        {!isLoading && !error && searchQuery && (
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Found {data?.memories?.length || 0} memories for &quot;{searchQuery}&quot;
            </p>
            {data?.memories?.map((memory: Memory) => (
              <div
                key={memory.memory_id}
                className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="secondary">{memory.memory_type}</Badge>
                  <span className="text-xs text-muted-foreground">
                    Confidence: {Math.round(memory.confidence * 100)}%
                  </span>
                </div>
                <p className="text-sm">{memory.content}</p>
                {memory.entities.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {memory.entities.map((entity) => (
                      <Badge key={entity} variant="outline" className="text-xs">
                        {entity}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {data?.memories?.length === 0 && (
              <p className="text-muted-foreground text-center py-8">
                No memories found matching your search.
              </p>
            )}
          </div>
        )}

        {!searchQuery && !isLoading && (
          <p className="text-muted-foreground text-center py-8">
            Enter a query above to search through your memories.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
