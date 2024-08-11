import { TreeDataNode } from "antd";
import type { SegmentedLabeledOption } from "antd/lib/segmented";

export type TreeKey = string | number;

export type TreeNode<T = any> = TreeDataNode & {
    key: TreeKey;
    children?: TreeNode[];
    data: T;
};

type AncestorMap = {
    [key: string]: TreeNode[];
};

export type View = SegmentedLabeledOption & {
    viewFactory: () => React.ReactNode;
};

export default abstract class Tree<T = any> {
    private nodes: TreeNode<T>[];
    private ancestorsByKey: { [key: TreeKey]: TreeNode<T>[] };
    public static ROOT = "_ROOT_";

    constructor(nodes: TreeNode<T>[]) {
        this.nodes = nodes;
        this.ancestorsByKey = Tree.mapNodeAncestors(nodes);
    }

    /**
     * Creates a mapping between a node (by key) and an array of its ancestors,
     * starting with the root node, and finishing with itself.
     * @param treeNodes
     * @returns A mapping from node to ancestors
     */
    private static mapNodeAncestors(rootNodes: TreeNode[]) {
        const branchMap: AncestorMap = {};
        const recurse = (nodes: TreeNode[], parents: TreeNode[] = []) => {
            for (const node of nodes) {
                const ancestry = [...parents, node];
                branchMap[String(node.key)] = ancestry;
                if (node.children) {
                    recurse(node.children, ancestry);
                }
            }
        };
        recurse(rootNodes);
        return branchMap;
    }

    getAncestorsByKey(key: TreeKey): TreeNode<T>[] {
        return this.ancestorsByKey[key] ?? [];
    }

    getNodeByKey(key: TreeKey): TreeNode<T> {
        const ancestors = this.ancestorsByKey[key];
        return ancestors[ancestors.length - 1];
    }

    getRoots(): TreeNode<T>[] {
        return this.nodes;
    }

    /**
     * Walk over the tree of node, yielding each node and its parent.
     *
     * @param nodes The nodes to walk over
     * @param parent The parent node (for if walking over a subtree)
     */
    *walk(
        nodes: TreeNode<T>[] | null = null,
        parent: TreeNode<T> | null = null,
    ): Generator<[TreeNode<T>, TreeNode<T> | null]> {
        nodes = nodes ?? this.nodes;
        for (const node of nodes) {
            if (node.children) {
                yield* this.walk(node.children, node);
            }
            yield [node, parent];
        }
    }

    abstract getViewsByKey(key: TreeKey): View[];
}
