from data_loader import load_all_data


def main():
    nodes, edges, od_pairs, release_curve = load_all_data()

    print("nodes:", nodes.shape)
    print("edges:", edges.shape)
    print("od_pairs:", od_pairs.shape)
    print("release_curve:", release_curve.shape)

    print("\nNodes columns:")
    print(nodes.columns.tolist())

    print("\nEdges columns:")
    print(edges.columns.tolist())

    print("\nOD pairs columns:")
    print(od_pairs.columns.tolist())

    print("\nRelease curve columns:")
    print(release_curve.columns.tolist())


if __name__ == "__main__":
    main()