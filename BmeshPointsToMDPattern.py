import bpy
import bmesh
import math

# アクティブオブジェクトがメッシュかどうか確認
obj = bpy.context.active_object
if obj is None or obj.type != 'MESH':
    print("アクティブオブジェクトがメッシュではありません。")
else:
    # BMeshを作成しオブジェクトのメッシュデータを読み込む
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    visited = set()    # 訪問済み頂点のセット
    dfs_order = []     # DFS順に頂点を格納するリスト

    # DFSアルゴリズム（スタック方式）の実装
    def dfs(start_vert):
        stack = [start_vert]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            dfs_order.append(current)
            # 隣接する未訪問の頂点をスタックに追加
            for edge in current.link_edges:
                other = edge.other_vert(current)
                if other not in visited:
                    stack.append(other)
    
    # すべての連結成分に対してDFSを実施
    for vert in bm.verts:
        if vert not in visited:
            dfs(vert)
    
    # 各頂点の座標を100倍し、小数点1位まで（小数点第2位以降切り捨て）に変換
    # 例: 1.2345 -> 123.45 -> 切り捨てで123.4
    coords_list = [
        (math.floor(v.co.x * 100 * 10) / 10, math.floor(v.co.y * 100 * 10) / 10, 0)
        for v in dfs_order
    ]
    
    # 累積的に頂点リストを生成し、各段階でMarvelous Designer用コード行を作成
    code_lines = []
    for i in range(1, len(coords_list) + 1):
        cumulative_tuple = tuple(coords_list[:i])
        line = "pattern_api.CreatePatternWithPoints(" + str(cumulative_tuple) + ")"
        code_lines.append(line)
    
    # コード行を改行で連結して1つの文字列にする
    code_str = "\n".join(code_lines)
    
    # ウィンドウマネージャ経由でクリップボードに格納
    bpy.context.window_manager.clipboard = code_str
    print("生成されたコードがクリップボードにコピーされました。")
    
    bm.free()
