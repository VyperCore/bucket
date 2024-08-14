import CoverageTree, { PointNode } from "./coveragetree";
import { Table, TableProps } from "antd";
import { view } from "../theme";
import { TreeKey } from "./tree";
import {Theme as ThemeType} from "@/theme";
import Color from "colorjs.io";
import Theme from "@/providers/Theme";

export type PointGridProps = {
    node: PointNode;
};

function getCoverageColumnConfig(theme: ThemeType, columnKey: string) {
    const good = new Color(theme.theme.colors.positivebg.value);
    const bad = new Color(theme.theme.colors.negativebg.value);
    const mix = Color.range(Color.mix(bad, good, 0.2, {space:'hsl'}), 
                            Color.mix(bad, good, 0.6, {space:'hsl'}),
                            {space:'hsl'});
    return {
        render: (ratio: number) => {
            if (Number.isNaN(ratio) || Object.is(ratio, -0)) {
                return '-';
            } else if (ratio < 0) {
                return '!!!';
            }
            return `${(Math.min(ratio, 1) * 100).toFixed(1)}%`;
        },
        onCell: (record: any) => {
            const ratio = record[columnKey];
            let backgroundColor = "unset";
            let fontWeight = "unset";
            if (ratio >= 1) {
                // >=1 if target is fully hit
                backgroundColor = good.toString();
            } else if (Number.isNaN(ratio) || Object.is(ratio, -0)) {
                // NaN if target is zero (don't care)
                // -0 if target is negative (illegal) and not hit
            } else if (ratio <= 0) {
                // <0 if target is negative (illegal) and hit
                backgroundColor = bad.toString();
                fontWeight = "bold"
            } else {
                // 0<x<1 if target is hit but not fully
                // Interpolate between bad and good, leaving some margin
                // so full hit and fully missed is distinguishable
                const clamped = Math.min(Math.max(ratio, 0), 1);
                backgroundColor = mix(clamped).toString();
            }
            return {
                style: {
                    backgroundColor,
                    fontWeight
                },
            }
        }
    }
}

/**
 * Splits strings into alpha and numeric portions before comparison
 * and tries to treat the numeric portions as numbers.
 */
function naturalCompare(a: String | Number, b: String | Number) {
    const aParts = a.toString().split(/(\d+)/g);
    const bParts = b.toString().split(/(\d+)/g);
    while (true) {
        const aPart = aParts.shift();
        const bPart = bParts.shift();

        if (aPart === undefined || bPart === undefined) {
            if (aPart !== undefined) {
                return 1;
            }
            if (bPart !== undefined) {
                return -1;
            }
            return NaN;
        }

        const numCompare = Number.parseInt(aPart) - Number.parseInt(bPart);
        if (!Number.isNaN(numCompare) && numCompare != 0) {
            return numCompare;
        }
        const strCompare = aPart.localeCompare(bPart);
        if (strCompare != 0) {
            return strCompare;
        }
    }
}

function getColumnCompare(columnKey: string) {
    return (a:any,b:any) => naturalCompare(a[columnKey], b[columnKey]);
}


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

    const getColumns = (theme: ThemeType): TableProps['columns'] => [
        {
            title: "Bucket",
            dataIndex: "key",
            key: "key",
        },
        {
            title: "Axes",
            children: axes.map(axis => {
                return {
                    title: axis.name,
                    dataIndex: axis.name,
                    key: axis.name,
                    filters: axis_values.slice(axis.value_start - axis_value_start, axis.value_end - axis_value_start).map(axis_value => ({
                        text: axis_value.value,
                        value: axis_value.value
                    })),
                    onFilter: (value, record) => record[axis.name] == value,
                    sorter: getColumnCompare(axis.name)
                }
            })
        },
        {
            title: "Goal",
            children: [
                {
                    title: "Name",
                    dataIndex: "goal_name",
                    key: "goal_name",
                    filters: goals.map(goal => ({
                        text: `${goal.name} - ${goal.description}`,
                        value: goal.name
                    })),
                    onFilter: (value, record) => record["goal_name"] == value,
                    sorter: getColumnCompare("goal_name")
                },
                {
                    title: "Target",
                    dataIndex: "target",
                    key: "target",
                    sorter: getColumnCompare('target')
                },
                {
                    title: "Hits",
                    dataIndex: "hits",
                    key: "hits",
                    sorter: getColumnCompare('hits')
                },
                {
                    title: "Hit %",
                    dataIndex: "hit_ratio",
                    key: "hit_ratio",
                    ...getCoverageColumnConfig(theme, "hit_ratio"),
                    sorter: getColumnCompare('hit_ratio')
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
        const datum: any = {
            key: bucket_hit.start,
            target: goal.target,
            hits: bucket_hit.hits,
            hit_ratio: bucket_hit.hits / goal.target,
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

    return <Theme.Consumer>
        {({ theme }) => {
            return <Table { ...view.body.content.table.props }
                key={node.key}
                columns={getColumns(theme)}
                dataSource={dataSource}
            />
        }}
    </Theme.Consumer>
}

export type PointSummaryGridProps = {
    tree: CoverageTree;
    node: PointNode;
    setSelectedTreeKeys: (newSelectedKeys: TreeKey[]) => void;
};


export function PointSummaryGrid({tree, node, setSelectedTreeKeys}: PointSummaryGridProps) {
    const getColumns = (theme: ThemeType): TableProps['columns'] => [
        {
            title: "Path",
            dataIndex: "path",
            key: "path",
            render: text => <a>{text}</a>,
            onCell: record => ({
                onClick: () => setSelectedTreeKeys([record.key]),
            }),
            sorter: getColumnCompare('path')
        },
        {
            title: "Description",
            dataIndex: "desc",
            key: "desc",
            sorter: getColumnCompare('desc')
        },
        {
            title: "Goal",
            children: [
                {
                    title: "Target",
                    dataIndex: "target",
                    key: "target",
                    sorter: getColumnCompare('target')
                },
                {
                    title: "Hits",
                    dataIndex: "hits",
                    key: "hits",
                    sorter: getColumnCompare('hits')
                },
                {
                    title: "Hit %",
                    dataIndex: "hit_ratio",
                    key: "hit_ratio",
                    ...getCoverageColumnConfig(theme, "hit_ratio"),
                    sorter: getColumnCompare('hit_ratio')
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
                    sorter: getColumnCompare('target_buckets')
                },
                {
                    title: "Hit",
                    dataIndex: "hit_buckets",
                    key: "hit_buckets",
                    sorter: getColumnCompare('hit_buckets')
                },
                {
                    title: "Full",
                    dataIndex: "full_buckets",
                    key: "full_buckets",
                    sorter: getColumnCompare('full_buckets')
                },
                {
                    title: "Hit %",
                    dataIndex: "buckets_hit_ratio",
                    key: "buckets_hit_ratio",
                    ...getCoverageColumnConfig(theme, "buckets_hit_ratio"),
                    sorter: getColumnCompare('buckets_hit_ratio')
                },
                {
                    title: "Full %",
                    dataIndex: "buckets_full_ratio",
                    key: "buckets_full_ratio",
                    ...getCoverageColumnConfig(theme, "buckets_full_ratio"),
                    sorter: getColumnCompare('buckets_full_ratio')
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

    return <Theme.Consumer>
        {({ theme }) => {
            return <Table { ...view.body.content.table.props }
                key={node.key}
                columns={getColumns(theme)}
                dataSource={dataSource}
            />
        }}
    </Theme.Consumer>
}
