-- =============================================================================
-- business_queries.sql
-- Customer Shopping Behavior — Advanced Business Queries
-- Covers business questions 6 – 8
-- Uses: CTEs, CASE statements, window functions (ROW_NUMBER, SUM OVER)
-- =============================================================================


-- =============================================================================
-- QUERY 6: Customer Segmentation — New / Returning / Loyal
-- Business Question: What share of customers fall into each loyalty tier?
-- Segments:
--   New       → previous_purchases = 1  (first-time or near-new buyers)
--   Returning → previous_purchases 2–10 (engaged but not yet loyal)
--   Loyal     → previous_purchases > 10 (high-frequency repeat customers)
--
-- Technique: CTE to compute the segment label, then aggregate in the outer
--            query so the CASE logic is written exactly once.
-- Why useful: Drives personalised messaging — e.g., win-back campaigns for
--             New, upsell for Returning, rewards for Loyal.
-- =============================================================================
WITH segmented AS (
    SELECT
        *,
        CASE
            WHEN previous_purchases = 1       THEN 'New'
            WHEN previous_purchases BETWEEN 2
                                    AND 10    THEN 'Returning'
            ELSE                                   'Loyal'
        END AS customer_segment
    FROM customer
)
SELECT
    customer_segment,
    COUNT(*)                          AS customer_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        1
    )                                 AS pct_of_total,
    ROUND(AVG(purchase_amount), 2)    AS avg_spend,
    ROUND(SUM(purchase_amount), 2)    AS total_revenue,
    ROUND(AVG(review_rating), 2)      AS avg_rating
FROM segmented
GROUP BY customer_segment
ORDER BY
    CASE customer_segment
        WHEN 'New'       THEN 1
        WHEN 'Returning' THEN 2
        WHEN 'Loyal'     THEN 3
    END;


-- =============================================================================
-- QUERY 7: Top 3 Products per Category (Window Function)
-- Business Question: Within each product category, which are the three
--                    best-selling items by number of orders?
-- Technique: ROW_NUMBER() OVER (PARTITION BY category ORDER BY total_orders DESC)
--            — assigns rank 1, 2, 3 within each category partition; the outer
--            WHERE filters to keep only ranks 1–3.
-- Why useful: Informs per-category inventory stocking and homepage merchandising
--             — show the right top-sellers inside each section of the site.
-- =============================================================================
WITH product_orders AS (
    -- Step 1: aggregate order counts and revenue per item/category
    SELECT
        category,
        item_purchased,
        COUNT(*)                        AS total_orders,
        ROUND(SUM(purchase_amount), 2)  AS total_revenue,
        ROUND(AVG(review_rating), 2)    AS avg_rating
    FROM customer
    GROUP BY category, item_purchased
),
ranked AS (
    -- Step 2: rank within each category
    SELECT
        category,
        item_purchased,
        total_orders,
        total_revenue,
        avg_rating,
        ROW_NUMBER() OVER (
            PARTITION BY category
            ORDER BY total_orders DESC, total_revenue DESC
        ) AS rank_in_category
    FROM product_orders
)
-- Step 3: keep only the top 3 per category
SELECT
    rank_in_category   AS rank,
    category,
    item_purchased,
    total_orders,
    total_revenue,
    avg_rating
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;


-- =============================================================================
-- QUERY 8: Revenue by Age Group
-- Business Question: Which customer age bracket generates the most revenue?
-- Age groups (engineered during cleaning):
--   18-25  Young Adults
--   26-35  Early Career
--   36-50  Mid-Career
--   51-65  Pre-Retirement
--   66+    Seniors
--
-- The ORDER BY uses a CASE expression to sort groups chronologically rather
-- than alphabetically, preserving the natural age progression in the output.
-- Why useful: Reveals which generation drives spend — guides channel choice
--             (e.g., mobile-first for 18-25, email for 51-65).
-- =============================================================================
SELECT
    age_group,
    COUNT(*)                                    AS customer_count,
    ROUND(AVG(purchase_amount), 2)              AS avg_spend,
    ROUND(SUM(purchase_amount), 2)              AS total_revenue,
    ROUND(
        100.0 * SUM(purchase_amount)
        / SUM(SUM(purchase_amount)) OVER (),
        1
    )                                           AS revenue_share_pct,
    -- Running cumulative revenue in age order
    ROUND(
        SUM(SUM(purchase_amount)) OVER (
            ORDER BY
                CASE age_group
                    WHEN '18-25' THEN 1
                    WHEN '26-35' THEN 2
                    WHEN '36-50' THEN 3
                    WHEN '51-65' THEN 4
                    WHEN '66+'   THEN 5
                END
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        2
    )                                           AS cumulative_revenue
FROM customer
GROUP BY age_group
ORDER BY
    CASE age_group
        WHEN '18-25' THEN 1
        WHEN '26-35' THEN 2
        WHEN '36-50' THEN 3
        WHEN '51-65' THEN 4
        WHEN '66+'   THEN 5
    END;
