from pr_analysis import get_unique_sorted_users, create_labels_filter_query, calculate_merge_times

def test_get_unique_sorted_users():
    all_pr_data = [
        {
            'allReviews': {
                'edges': [
                    {'node': {'author': {'login': 'reviewer-1'}}},
                    {'node': {'author': {'login': 'reviewer-2'}}},
                    {'node': {'author': {'login': 'reviewer-3'}}},
                    {'node': {'author': {'login': 'reviewer-1'}}},
                    {'node': {'author': {'login': 'reviewer-3'}}},
                ]
            },
            'approvedReviews': {
                'edges': [
                    {'node': {'author': {'login': 'reviewer-1'}}},
                    {'node': {'author': {'login': 'reviewer-2'}}}
                ]
            }
        },
        {
            'allReviews': {
                'edges': []
            },
            'approvedReviews': {
                'edges': []
            }
        },
        {
            'allReviews': {
                'edges': [
                    {'node': {'author': {'login': 'reviewer-1'}}}
                ]
            },
            'approvedReviews': {
                'edges': [
                    {'node': {'author': {'login': 'reviewer-2'}}}
                ]
            }
        }
    ]

    code_reviewers = get_unique_sorted_users(all_pr_data, 'allReviews')
    approved_reviewers = get_unique_sorted_users(all_pr_data, 'approvedReviews')
    assert code_reviewers == ['reviewer-1, reviewer-2, reviewer-3', '', 'reviewer-1']
    assert approved_reviewers == ['reviewer-1, reviewer-2', '', 'reviewer-2']

def test_create_labels_filter_query():
    # no labels
    pr_labels = []
    assert create_labels_filter_query(pr_labels) == ''
    # one label
    pr_labels = ['label1']
    assert create_labels_filter_query(pr_labels) == 'labels: ["label1"],'
    # multiple labels
    pr_labels = ['label1', 'label2', 'label3']
    assert create_labels_filter_query(pr_labels) == 'labels: ["label1", "label2", "label3"],'

def test_calculate_merge_times():
    # no data
    all_pr_data = []
    assert calculate_merge_times(all_pr_data) == []

    # pull request merged on the same day
    all_pr_data = [
    {
        "number": 53179,
        "title": "Enhancing Performance and Functionality",
        "state": "MERGED",
        "author": {
        "login": "meh-user"
        },
        "createdAt": "2023-07-25T20:22:52Z",
        "closedAt": "2023-07-25T21:10:23Z",
        "changedFiles": 4,
        "timelineItems": {
        "totalCount": 7
        },
        "approvedReviews": {
        "edges": []
        },
        "allReviews": {
        "edges": []
        },
        "mergedBy": {
            "login": "awesome-user"
        }
    }]
    assert calculate_merge_times(all_pr_data) == ['same day']

    # pull request merged after one day
    all_pr_data = [{
        "number": 53179,
        "title": "Enhancing Performance and Functionality",
        "state": "MERGED",
        "author": {
        "login": "meh-user"
        },
        "createdAt": "2023-07-25T20:22:52Z",
        "closedAt": "2023-07-26T21:10:23Z",
        "changedFiles": 4,
        "timelineItems": {
        "totalCount": 7
        },
        "approvedReviews": {
        "edges": []
        },
        "allReviews": {
        "edges": []
        },
        "mergedBy": {
            "login": "awesome-user"
        }
    }]
    assert calculate_merge_times(all_pr_data) == ['1 day']

    # pull request merged after multiple days
    all_pr_data = [{
        "number": 53179,
        "title": "Enhancing Performance and Functionality",
        "state": "MERGED",
        "author": {
        "login": "meh-user"
        },
        "createdAt": "2023-07-25T20:22:52Z",
        "closedAt": "2023-07-30T21:10:23Z",
        "changedFiles": 4,
        "timelineItems": {
        "totalCount": 7
        },
        "approvedReviews": {
        "edges": []
        },
        "allReviews": {
        "edges": []
        },
        "mergedBy": {
            "login": "awesome-user"
        }
    },
    {
        "number": 53179,
        "title": "Enhancing Performance and Functionality Part 2",
        "state": "MERGED",
        "author": {
        "login": "meh-user"
        },
        "createdAt": "2023-07-25T20:22:52Z",
        "closedAt": "2023-08-30T21:10:23Z",
        "changedFiles": 4,
        "timelineItems": {
        "totalCount": 7
        },
        "approvedReviews": {
        "edges": []
        },
        "allReviews": {
        "edges": []
        },
        "mergedBy": {
            "login": "awesome-user"
        }
    }]
    assert calculate_merge_times(all_pr_data) == ['5 days', '36 days']
