import { TreeNode } from "../../lib/tree";

const treeMock: TreeNode[] = [
    {
        title: "parent 1",
        key: "0-0",
        children: [
            {
                title: "parent 1-0",
                key: "0-0-0",
                children: [
                    {
                        title: "leaf",
                        key: "0-0-0-0",
                    },
                    {
                        title: "multiple line title, multiple line title",
                        key: "0-0-0-1",
                    },
                    {
                        title: "my very long title without breaks",
                        key: "0-0-0-2",
                    },
                ],
            },
            {
                title: "parent 1-1",
                key: "0-0-1",
                children: [
                    {
                        title: "leaf",
                        key: "0-0-1-0",
                    },
                ],
            },
            {
                title: "parent 1-2",
                key: "0-0-2",
                children: [
                    {
                        title: "leaf-0",
                        key: "0-0-2-0",
                    },
                    {
                        title: "leaf-1",
                        key: "0-0-2-1",
                    },
                ],
            },
        ],
    },
    {
        title: "parent 2",
        key: "0-1",
        children: [
            {
                title: "parent 2-0",
                key: "0-1-0",
                children: [
                    {
                        title: "leaf-0",
                        key: "0-1-0-0",
                    },
                    {
                        title: "leaf-1",
                        key: "0-1-0-1",
                    },
                ],
            },
        ],
    },
];
export default treeMock;
