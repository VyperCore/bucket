import CoverageTree, { PointNode } from "./coveragetree";
import { Table, TableProps } from "antd";
import { view } from "../theme";
import { TreeKey } from "./tree";

export type PointGridProps = {
    node: PointNode;
};


export function PointGrid({node}: PointGridProps) {
    const pointData = node.data;
    const reading = pointData.reading;
    
    let dataSource: {}[] = [];
    const {
        axis_start,
        axis_end,
        axis_value_start,
        axis_value_end,
        bucket_start,
        bucket_end,
        goal_start,
        goal_end,
    } = pointData.point;
    const axes = Array.from(
        pointData.reading.iter_axes(axis_start, axis_end),
    );

    const axis_values = Array.from(
        pointData.reading.iter_axis_values(
            axis_value_start,
            axis_value_end,
        ),
    );
    const goals = Array.from(
        pointData.reading.iter_goals(goal_start, goal_end),
    );

    const columns = [
        {
            title: "Bucket",
            dataIndex: "key",
            key: "key",
        },
        {
            title: "Axes",
            children: axes.map(axis => ({
                title: axis.name,
                dataIndex: axis.name,
                key: axis.name,
            }))
        },
        {
            title: "Goal",
            children: [
                {
                    title: "Name",
                    dataIndex: "goal_name",
                    key: "goal_name",
                },
                {
                    title: "Target",
                    dataIndex: "target",
                    key: "target",
                },
                {
                    title: "Hits",
                    dataIndex: "hits",
                    key: "hits",
                },
            ]
        }
    ]


    const bucket_hits = reading.iter_bucket_hits(bucket_start, bucket_end);
    for (const bucket_goal of reading.iter_bucket_goals(
        bucket_start,
        bucket_end,
    )) {
        const bucket_hit = bucket_hits.next().value;
        const goal = goals[bucket_goal.goal - goal_start];
        const datum = {
            key: bucket_hit.start,
            hits: bucket_hit.hits,
            target: goal.target,
            goal_name: goal.name
        };

        let offset = bucket_goal.start - bucket_start;
        for (let axis_idx = axes.length - 1; axis_idx >= 0; axis_idx--) {
            const axis = axes[axis_idx];
            const axis_offset = axis.value_start - axis_value_start;
            const axis_size = axis.value_end - axis.value_start;
            const axis_value_idx = offset % axis_size;
            datum[axis.name] = axis_values[axis_offset + axis_value_idx].value;
            offset = Math.floor(offset / axis_size);
        }

        dataSource.push(datum);
    }

    return <Table { ...view.body.content.table.props }
        columns={columns}
        dataSource={dataSource}
    />
}

export type PointSummaryGridProps = {
    tree: CoverageTree;
    node: PointNode;
    setSelectedTreeKeys: (newSelectedKeys: TreeKey[]) => void;
};


export function PointSummaryGrid({tree, node, setSelectedTreeKeys}: PointSummaryGridProps) {
    const pointData = node.data;
    const reading = pointData.reading;
    const columns: TableProps['columns'] = [
        {
            title: "Path",
            dataIndex: "path",
            key: "path",
            render: text => <a>{text}</a>,
            onCell: record => ({
                onClick: () => setSelectedTreeKeys([record.key]), 
            })
        },
        {
            title: "Description",
            dataIndex: "desc",
            key: "desc",
        },
        {
            title: "Goal",
            children: [
                {
                    title: "Target",
                    dataIndex: "target",
                    key: "target",
                },
                {
                    title: "Hits",
                    dataIndex: "hits",
                    key: "hits",
                },
                {
                    title: "Hit %",
                    dataIndex: "hit_ratio",
                    key: "hit_ratio",
                    render: v => `${(100 * v).toFixed(1)}%`,
                },
            ]
        },
        {
            title: "Buckets",
            children: [
                {
                    title: "Target",
                    dataIndex: "target_buckets",
                    key: "target_buckets",
                },
                {
                    title: "Hit",
                    dataIndex: "hit_buckets",
                    key: "hit_buckets",
                },
                {
                    title: "Full",
                    dataIndex: "full_buckets",
                    key: "full_buckets",
                },
                {
                    title: "Hit %",
                    dataIndex: "buckets_hit_ratio",
                    key: "buckets_hit_ratio",
                    render: v => `${(100 * v).toFixed(1)}%`,
                },
                {
                    title: "Full %",
                    dataIndex: "buckets_full_ratio",
                    key: "buckets_full_ratio",
                    render: v => `${(100 * v).toFixed(1)}%`,
                },
            ]
        }
    ];
    const dataSource: {}[] = [];

    const gather = (n: PointNode):PointNode[] => [n].concat(...n.children?.map(gather) ?? [])

    
    const isRoot = node.key == CoverageTree.ROOT;

    const root = isRoot ? null : [node];
    const nodePath = tree.getAncestorsByKey(node.key)
    for (const [subNode, _parent] of tree.walk(root)) {
        const path = tree.getAncestorsByKey(subNode.key)
                          .slice(nodePath.length - 1)
                          .map(n => n.title as string).join(' / ')
        const {point, point_hit} = subNode.data;

        const hit_ratio =
            point_hit.hits / point.target;
        const buckets_hit_ratio =
            point_hit.hit_buckets / point.target_buckets;
        const buckets_full_ratio =
            point_hit.full_buckets / point.target_buckets;

        dataSource.push({
            key: subNode.key,
            path: path,
            desc: point.description,
            target: point.target,
            hits: point_hit.hits,
            target_buckets: point.target_buckets,
            hit_buckets: point_hit.hit_buckets,
            full_buckets: point_hit.full_buckets,
            hit_ratio,
            buckets_hit_ratio,
            buckets_full_ratio,
        });
    }

    // for (const child of gather(node)) {
    //     const {point, point_hit} = child.data;
    //     dataSource.push({
    //         key: `${point.start}-${point.end}`,
    //         name: point.name,
    //         desc: point.description,
    //         target: point.target,
    //         hits: point_hit.hits,
    //         target_buckets: point.target_buckets,
    //         hit_buckets: point_hit.hit_buckets,
    //     });
    // }

    // const point_hits = reading.iter_point_hits(start, end, depth);
    // for (const point of reading.iter_points(start, end, depth)) {
    //     const point_hit = point_hits.next().value;
    //     dataSource.push({
    //         key: `${point.start}-${point.end}`,
    //         name: point.name,
    //         desc: point.description,
    //         target: point.target,
    //         hits: point_hit.hits,
    //         target_buckets: point.target_buckets,
    //         hit_buckets: point_hit.hit_buckets,
    //     });
    // }
    return <Table { ...view.body.content.table.props }
        columns={columns}
        dataSource={dataSource}
    />
}
