from pr_analysis import get_unique_sorted_users, create_labels_filter_query

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
