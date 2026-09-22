-- =============================================================================
-- business_queries.sql
-- Customer Shopping Behavior — Advanced Business Queries
-- Q6–Q8 use CTEs and window functions.
-- =============================================================================

-- Q6: Customer segmentation
-- previous_purchases is the number of purchases before the current record:
-- 0 = New, 1–10 = Returning, >10 = Loyal.
WITH segmented AS (
    SELECT
        *,
        CASE
            WHEN previous_purchases = 0 THEN 'New'
            WHEN previous_purchases BETWEEN 1 AND 10 THEN 'Returning'
            ELSE 'Loyal'
        END AS customer_segment
    FROM customer
)
SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    ROUND(AVG(purchase_amount), 2) AS avg_purchase_amount,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(AVG(review_rating), 2) AS avg_rating
FROM segmented
GROUP BY customer_segment
ORDER BY CASE customer_segment
    WHEN 'New' THEN 1
    WHEN 'Returning' THEN 2
    WHEN 'Loyal' THEN 3
END;

-- Q7: Top 3 products per category by customer-record count.
-- DENSE_RANK keeps ties at the same rank.
WITH product_counts AS (
    SELECT
        category,
        item_purchased,
        COUNT(*) AS customer_count,
        ROUND(SUM(purchase_amount), 2) AS total_revenue,
        ROUND(AVG(review_rating), 2) AS avg_rating
    FROM customer
    GROUP BY category, item_purchased
),
ranked AS (
    SELECT
        *,
        DENSE_RANK() OVER (
            PARTITION BY category
            ORDER BY customer_count DESC
        ) AS rank_in_category
    FROM product_counts
)
SELECT
    rank_in_category AS rank,
    category,
    item_purchased,
    customer_count,
    total_revenue,
    avg_rating
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category, item_purchased;

-- Q8: Revenue by age group
SELECT
    age_group,
    COUNT(*) AS customer_count,
    ROUND(AVG(purchase_amount), 2) AS avg_purchase_amount,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(purchase_amount)
        / SUM(SUM(purchase_amount)) OVER (),
        1
    ) AS revenue_share_pct,
    ROUND(
        SUM(SUM(purchase_amount)) OVER (
            ORDER BY CASE age_group
                WHEN '18-25' THEN 1
                WHEN '26-35' THEN 2
                WHEN '36-50' THEN 3
                WHEN '51-65' THEN 4
                WHEN '66+' THEN 5
            END
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    ) AS cumulative_revenue
FROM customer
GROUP BY age_group
ORDER BY CASE age_group
    WHEN '18-25' THEN 1
    WHEN '26-35' THEN 2
    WHEN '36-50' THEN 3
    WHEN '51-65' THEN 4
    WHEN '66+' THEN 5
END;
