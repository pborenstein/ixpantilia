#!/usr/bin/env python3
"""
Simple HTML5 Canvas visualization as fallback.
"""
import json
from pathlib import Path
from src.visualizer.visualizer import PersonalKnowledgeGraphVisualizer


def create_canvas_viz(graph_data: dict, output_path: Path):
    """Create HTML5 Canvas visualization."""
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Knowledge Graph - Canvas</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
        }}
        
        #canvas {{
            border: 1px solid #666;
            background: #000;
            cursor: crosshair;
        }}
        
        .info {{
            margin: 10px 0;
            font-size: 14px;
        }}
        
        .node-info {{
            margin-top: 20px;
            padding: 10px;
            background: #333;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <h1>Personal Knowledge Graph (Canvas)</h1>
    <div class="info">Nodes: {len(graph_data['nodes'])}, Edges: {len(graph_data['edges'])}</div>
    
    <canvas id="canvas" width="1200" height="800"></canvas>
    
    <div class="node-info">
        <h3>Selected Node</h3>
        <div id="selected-info">Click a node to see details</div>
    </div>

    <script>
        const data = {json.dumps(graph_data, indent=2)};
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        const colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];
        
        function drawGraph() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw edges
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 1;
            ctx.globalAlpha = 0.3;
            
            data.edges.forEach(edge => {{
                const source = data.nodes.find(n => n.id === edge.source);
                const target = data.nodes.find(n => n.id === edge.target);
                
                if (source && target) {{
                    ctx.beginPath();
                    ctx.moveTo(source.x, source.y);
                    ctx.lineTo(target.x, target.y);
                    ctx.stroke();
                }}
            }});
            
            ctx.globalAlpha = 1;
            
            // Draw nodes
            data.nodes.forEach(node => {{
                const radius = Math.max(4, Math.sqrt(node.content_length / 200) + 3);
                const color = colors[node.cluster % colors.length];
                
                ctx.fillStyle = color;
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 1;
                
                ctx.beginPath();
                ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
                ctx.fill();
                ctx.stroke();
                
                // Draw labels for larger nodes
                if (node.content_length > 1000) {{
                    ctx.fillStyle = '#ddd';
                    ctx.font = '8px Arial';
                    ctx.textAlign = 'center';
                    
                    let title = node.title;
                    if (title.length > 20) title = title.substring(0, 17) + '...';
                    
                    ctx.fillText(title, node.x, node.y - radius - 5);
                }}
            }});
        }}
        
        function findNodeAtPosition(x, y) {{
            for (let node of data.nodes) {{
                const radius = Math.max(4, Math.sqrt(node.content_length / 200) + 3);
                const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2);
                if (distance <= radius) {{
                    return node;
                }}
            }}
            return null;
        }}
        
        canvas.addEventListener('click', function(event) {{
            const rect = canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            const clickedNode = findNodeAtPosition(x, y);
            if (clickedNode) {{
                document.getElementById('selected-info').innerHTML = `
                    <h4>${{clickedNode.title}}</h4>
                    <p><strong>Path:</strong> ${{clickedNode.relative_path}}</p>
                    <p><strong>Domain:</strong> ${{clickedNode.domain}}</p>
                    <p><strong>Cluster:</strong> ${{clickedNode.cluster}}</p>
                    <p><strong>Size:</strong> ${{clickedNode.content_length}} chars</p>
                    ${{clickedNode.tags.length > 0 ? `<p><strong>Tags:</strong> ${{clickedNode.tags.join(', ')}}</p>` : ''}}
                `;
            }}
        }});
        
        console.log('Drawing graph...');
        drawGraph();
        console.log('Canvas visualization complete');
    </script>
</body>
</html>"""
    
    with open(output_path, 'w') as f:
        f.write(html)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from src.config import ConfigManager

    config = ConfigManager()
    vault_root = config.get_vault_path()

    if vault_root is None:
        print("Error: No vault path configured.")
        print("Please set the vault path first:")
        print("  uv run main.py set-vault ~/Obsidian/amoxtli")
        sys.exit(1)

    visualizer = PersonalKnowledgeGraphVisualizer(
        vault_root=vault_root,
        embeddings_dir=Path("embeddings/")
    )

    graph_data = visualizer.generate_graph_data(similarity_threshold=0.4, num_clusters=6)
    create_canvas_viz(graph_data, Path("visualizations/canvas_graph.html"))
    print("Canvas visualization: visualizations/canvas_graph.html")