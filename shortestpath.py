import matplotlib.pyplot as plt
import networkx as nx

n = 10  # 10 nodes
m = 20  # 20 edges
seed = 20160  # seed random number generators for reproducibility

# Use seed for reproducibility
G = nx.gnm_random_graph(n, m, seed=seed)

# some properties
print("node degree clustering")
for v in nx.nodes(G):
    print(f"{v} {nx.degree(G, v)} {nx.clustering(G, v)}")


print()
print("the adjacency list")
for line in nx.generate_adjlist(G):
    print(line)

pos = nx.spring_layout(G, seed=seed)  # Seed for reproducible layout
nx.draw_networkx(G, pos=pos, with_labels=True)
plt.show()


nr,nc = 9, 9
c= 0
data = {}
for i in range(nr):
    for j in range(nc):
        data[c] = (i,j)
        c+=1

for c,(i,j) in data.items():
    plt.scatter(i,j,s=100)
    plt.text(i,j,s=str(c))

plt.show()
