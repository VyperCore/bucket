import { Layout, Tree as AntTree, Input } from "antd";
import { ReactNode, useMemo, useState } from "react";
import { view } from "../../theme";
import Tree, { TreeKey, TreeNode } from "../../lib/tree";

/**
 * Processes a tree of nodes and applies a formatter to the tile of each.
 *
 * @param tree the tree to format
 * @param nodeTitleFormatter the formatter to apply
 * @returns a formatted tree of nodes
 */
function treeTitleFormatter(
    tree: Tree,
    nodeTitleFormatter: (treeNode: TreeNode) => ReactNode,
) {
    const callback = (treeNode: TreeNode): TreeNode => {
        return {
            ...treeNode,
            title: nodeTitleFormatter(treeNode),
            children: treeNode.children?.map(callback),
        };
    };
    return tree.getRoots().map(callback);
}

/**
 * Creates a title formatter based on a search value.
 *
 * @param searchValue the value being searched
 * @returns a formatted title with the search value highlighted
 */
function searchNodeTitleFormatterFactory(searchValue: string) {
    return (treeNode: TreeNode) => {
        const strTitle = treeNode.title as string;
        const index = strTitle.indexOf(searchValue);
        const beforeStr = strTitle.substring(0, index);
        const afterStr = strTitle.slice(index + searchValue.length);
        const title =
            index > -1 ? (
                <span>
                    {beforeStr}
                    <span {...view.sider.tree.searchlight.props}>
                        {searchValue}
                    </span>
                    {afterStr}
                </span>
            ) : (
                <span>{strTitle}</span>
            );
        return title;
    };
}

export type SiderProps = {
    tree: Tree;
    selectedTreeKeys: TreeKey[];
    expandedTreeKeys: TreeKey[];
    autoExpandTreeParent: boolean;
    setAutoExpandTreeParent: (newValue: boolean) => void;
    setSelectedTreeKeys: (newSelectedKeys: TreeKey[]) => void;
    setExpandedTreeKeys: (newExpandedKeys: TreeKey[]) => void;
};

export default function Sider({
    tree,
    selectedTreeKeys,
    expandedTreeKeys,
    autoExpandTreeParent,
    setAutoExpandTreeParent,
    setSelectedTreeKeys,
    setExpandedTreeKeys,
}: SiderProps) {
    const [searchValue, setSearchValue] = useState("");

    const onExpand = (newExpandedKeys: React.Key[]) => {
        setExpandedTreeKeys(newExpandedKeys as TreeKey[]);
        setAutoExpandTreeParent(false);
    };

    const onSelect = (newSelectedKeys: React.Key[]) => {
        setSelectedTreeKeys(newSelectedKeys as TreeKey[]);
    };

    const onSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { value } = e.target;
        const newExpandedKeys = new Set<TreeKey>();
        for (const [node, parent] of tree.walk()) {
            const strTitle = node.title as string;
            if (strTitle.includes(value) && parent !== null) {
                newExpandedKeys.add(parent.key);
            }
        }
        setExpandedTreeKeys(Array.from(newExpandedKeys));
        setSearchValue(value);
        setAutoExpandTreeParent(true);
    };

    const formattedTreeData = useMemo(() => {
        return treeTitleFormatter(
            tree,
            searchNodeTitleFormatterFactory(searchValue),
        );
    }, [searchValue, tree]);

    return (
        <Layout.Sider {...view.sider.props}>
            <Input {...view.sider.search.props} onChange={onSearchChange} />
            <AntTree
                {...view.sider.tree.props}
                onExpand={onExpand}
                onSelect={onSelect}
                selectedKeys={selectedTreeKeys}
                expandedKeys={expandedTreeKeys}
                autoExpandParent={autoExpandTreeParent}
                treeData={formattedTreeData}
            />
        </Layout.Sider>
    );
}
