-- =============================================================================
-- data_analysis.sql
-- Customer Shopping Behavior — Exploratory & Analytical Queries
-- Each row represents one customer record in the supplied dataset.
-- =============================================================================

-- Q1: Revenue and customer count by gender
SELECT
    gender,
    COUNT(*) AS customer_count,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(AVG(purchase_amount), 2) AS avg_purchase_amount
FROM customer
GROUP BY gender
ORDER BY total_revenue DESC;

-- Q2: Discounted high-value customer records
SELECT
    customer_id,
    gender,
    age,
    age_group,
    item_purchased,
    category,
    purchase_amount,
    payment_method,
    subscription_status
FROM customer
WHERE discount_applied = 1
  AND purchase_amount > (SELECT AVG(purchase_amount) FROM customer)
ORDER BY purchase_amount DESC;

-- Q3: Top 5 products by average review rating.
-- Minimum 5 customer records prevents a single observation dominating the list.
SELECT
    item_purchased,
    category,
    COUNT(*) AS customer_count,
    ROUND(AVG(review_rating), 2) AS avg_rating,
    ROUND(MIN(review_rating), 2) AS min_rating,
    ROUND(MAX(review_rating), 2) AS max_rating
FROM customer
GROUP BY item_purchased, category
HAVING COUNT(*) >= 5
ORDER BY avg_rating DESC, customer_count DESC
LIMIT 5;

-- Q4: Standard vs Express purchase metrics
SELECT
    shipping_type,
    COUNT(*) AS customer_count,
    ROUND(AVG(purchase_amount), 2) AS avg_purchase_amount,
    ROUND(MIN(purchase_amount), 2) AS min_purchase_amount,
    ROUND(MAX(purchase_amount), 2) AS max_purchase_amount,
    ROUND(SUM(purchase_amount), 2) AS total_revenue
FROM customer
WHERE shipping_type IN ('Standard', 'Express')
GROUP BY shipping_type
ORDER BY avg_purchase_amount DESC;

-- Q5: Subscriber vs non-subscriber metrics
SELECT
    CASE subscription_status
        WHEN 1 THEN 'Subscriber'
        WHEN 0 THEN 'Non-Subscriber'
    END AS subscriber_label,
    COUNT(*) AS customer_count,
    ROUND(AVG(purchase_amount), 2) AS avg_purchase_amount,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(
        100.0 * SUM(purchase_amount) / SUM(SUM(purchase_amount)) OVER (),
        1
    ) AS revenue_share_pct
FROM customer
GROUP BY subscription_status
ORDER BY subscription_status DESC;
