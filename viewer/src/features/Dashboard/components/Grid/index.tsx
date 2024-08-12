import { PointData } from "../../lib/coveragetree";
import { Table } from "antd";
import { view } from "../../theme";

export type GridProps = {
    summary: boolean;
    pointData: PointData;
};

export default function Grid({ summary, pointData }: GridProps) {
    let columns = [];
    let data: {}[] = [];
    const reading = pointData.reading;

    if (summary) {
        columns = [
            {
                title: "Name",
                dataIndex: "name",
                key: "name",
            },
            {
                title: "Description",
                dataIndex: "desc",
                key: "desc",
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
        ];
        const { start, end, depth } = pointData.point;
        const point_hits = reading.iter_point_hits(start, end, depth);
        for (const point of reading.iter_points(start, end, depth)) {
            const point_hit = point_hits.next().value;
            data.push({
                key: `${point.start}-${point.end}`,
                name: point.name,
                desc: point.description,
                target: point.target,
                hits: point_hit.hits,
                target_buckets: point.target_buckets,
                hit_buckets: point_hit.hit_buckets,
            });
        }
    } else {
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

        columns.push({
            title: "Bucket",
            dataIndex: "key",
            key: "key",
        });
        for (const axis of axes) {
            columns.push({
                title: axis.name,
                dataIndex: axis.name,
                key: axis.name,
            });
        }
        columns.push(
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
        );

        const bucket_hits = reading.iter_bucket_hits(bucket_start, bucket_end);
        for (const bucket_goal of reading.iter_bucket_goals(
            bucket_start,
            bucket_end,
        )) {
            const bucket_hit = bucket_hits.next().value;
            const datum = {
                key: bucket_hit.start,
                hits: bucket_hit.hits,
                target: goals[bucket_goal.goal - goal_start].target,
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

            data.push(datum);
        }
    }
    return (
        <Table
            columns={columns}
            dataSource={data} /* virtual={true} scroll={{ x: 0, y: 0 }}*/
        />
    );
}
