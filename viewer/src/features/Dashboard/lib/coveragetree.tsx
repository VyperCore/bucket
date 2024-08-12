import { LayoutOutlined, TableOutlined } from "@ant-design/icons";
import Tree, { TreeKey, TreeNode, View } from "./tree";
import {PointGrid, PointSummaryGrid} from "./coveragegrid";

export type PointData = {
    reading: Reading;
    point: PointTuple;
    point_hit: PointHitTuple;
};

export type PointNode = TreeNode<PointData>;

export default class CoverageTree extends Tree<PointData> {
    static fromReadings(readings: Reading[]): CoverageTree {
        // Record the tree and stack of current ancestors
        const tree: TreeNode[] = [];
        const stack: TreeNode[] = [];

        for (const [i, reading] of readings.entries()) {
            // Iterate over the points, building up a tree
            const point_hits = reading.iter_point_hits();
            for (const point of reading.iter_points()) {
                const point_hit = point_hits.next().value;
                const done = point_hit.full_buckets == point.target_buckets;
                console.log(
                    point.target_buckets,
                    point_hit.full_buckets,
                    point_hit.hit_buckets,
                    point_hit.hits,
                    point.target,
                );

                const dataNode: TreeNode<PointData> = {
                    // title: `${percentFull.toFixed(1)}%/${percentHit.toFixed(
                    //     1,
                    // )}%: ${point.name}`,
                    title: point.name,
                    key: `${i}-${point.start}-${point.end}`,
                    children: [],
                    data: {
                        reading,
                        point,
                        point_hit,
                    },
                    // icon: done ? <LayoutOutlined /> : <TableOutlined />,
                };
                // Discard anything below parent
                stack.splice(point.depth);
                if (point.depth === 0) {
                    // Add as root
                    tree.push(dataNode);
                } else {
                    // Add to parent as child
                    stack[point.depth - 1].children?.push(dataNode);
                }
                // Record in stack
                stack.push(dataNode);
            }
        }
        return new CoverageTree(tree);
    }

    getViewsByKey(key: TreeKey): View[] {
        const node = this.getNodeByKey(key);
        if (node.children?.length) {
            return [
                {
                    value: "Summary",
                    icon: <TableOutlined />,
                    viewFactory: () => (
                        <PointSummaryGrid tree={this} node={node} />
                    ),
                },
            ];
        } else {
            return [
                {
                    value: "Point",
                    icon: <TableOutlined />,
                    viewFactory: () => (
                        <PointGrid node={node} />
                    ),
                },
                {
                    value: "Pivot",
                    icon: <LayoutOutlined />,
                    viewFactory: () => <LayoutOutlined />,
                },
            ];
        }
    }
}
