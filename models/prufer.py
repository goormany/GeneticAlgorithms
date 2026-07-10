class PruferCode:
    @staticmethod
    def edges_to_code(n: int, edges: list[tuple[int, int]]) -> list[int]:
        if n <= 2:
            return []
        
        degree = [0] * (n + 1)
        adjacency = [set() for _ in range(n + 1)]
        
        for u, v in edges:
            degree[u] += 1
            degree[v] += 1
            adjacency[u].add(v)
            adjacency[v].add(u)
        
        prufer = []
        for _ in range(n-2):
            leaf = None
            for v in range(1, n + 1):
                if degree[v] == 1:
                    leaf = v
                    break
            
            neighbor = adjacency[leaf].pop()
            prufer.append(neighbor)
            
            adjacency[neighbor].remove(leaf)
            degree[leaf] -= 1
            degree[neighbor] -= 1
            
        return prufer
    
    @staticmethod
    def code_to_edges(n: int, code: list[int]) -> list[tuple[int, int]]:
        if n == 1:
            return []
        
        if n == 2:
            return [(1, 2)]
        
        degree = [1] * (n+1)
        degree[0] = 0
        
        for node in code:
            degree[node] += 1
        
        edges = []
        
        for node in code:
            for leaf in range(1, n+1):
                if degree[leaf] == 1:
                    edges.append((leaf, node))
                
                    degree[leaf] -= 1        
                    degree[node] -= 1
                    break
        
        remaining = [v for v in range(1, n + 1) if degree[v] == 1]
        if len(remaining) == 2:
            edges.append((remaining[0], remaining[1]))
        
        return edges

    @staticmethod
    def is_valid_prufer_code(n: int, code: list[int]) -> bool:
        if len(code) != n - 2:
            return False
        
        for node in code:
            if node < 1 or node > n:
                return False
            
        return True