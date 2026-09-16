-- =============================================================================
-- data_analysis.sql
-- Customer Shopping Behavior — Exploratory & Analytical Queries
-- Covers business questions 1 – 5
-- =============================================================================


-- =============================================================================
-- QUERY 1: Revenue by Gender
-- Business Question: How much total revenue does each gender generate?
-- Why useful: Identifies which gender drives more spending — informs targeted
--             marketing budgets and product assortment decisions.
-- =============================================================================
SELECT
    gender,
    COUNT(*)                        AS total_orders,
    ROUND(SUM(purchase_amount), 2)  AS total_revenue,
    ROUND(AVG(purchase_amount), 2)  AS avg_order_value
FROM customer
GROUP BY gender
ORDER BY total_revenue DESC;


-- =============================================================================
-- QUERY 2: Discounted High-Spenders
-- Business Question: Which customers used a discount AND spent above the
--                    overall average purchase amount?
-- Why useful: These customers respond to promotions but already spend heavily —
--             prime candidates for loyalty/VIP programmes rather than blanket
--             discounting.
-- =============================================================================
SELECT
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
  AND purchase_amount > (
          SELECT AVG(purchase_amount)
          FROM   customer
      )
ORDER BY purchase_amount DESC;


-- =============================================================================
-- QUERY 3: Top 5 Products by Average Review Rating
-- Business Question: Which are the five best-rated products?
-- Why useful: Highlights products worth promoting, cross-selling, or using in
--             social proof campaigns.
-- Note: We filter to products with at least 5 reviews to avoid a single
--       perfect rating inflating the rank.
-- =============================================================================
SELECT
    item_purchased,
    category,
    COUNT(*)                          AS total_reviews,
    ROUND(AVG(review_rating), 2)      AS avg_rating,
    ROUND(MIN(review_rating), 2)      AS min_rating,
    ROUND(MAX(review_rating), 2)      AS max_rating
FROM customer
GROUP BY item_purchased, category
HAVING COUNT(*) >= 5
ORDER BY avg_rating DESC, total_reviews DESC
LIMIT 5;


-- =============================================================================
-- QUERY 4: Shipping Type Spend — Standard vs Express
-- Business Question: Is there a meaningful spend difference between customers
--                    choosing Standard and Express shipping?
-- Why useful: Higher spenders may self-select into faster delivery — informs
--             free-shipping thresholds and upsell opportunities.
-- =============================================================================
SELECT
    shipping_type,
    COUNT(*)                          AS order_count,
    ROUND(AVG(purchase_amount), 2)    AS avg_spend,
    ROUND(MIN(purchase_amount), 2)    AS min_spend,
    ROUND(MAX(purchase_amount), 2)    AS max_spend,
    ROUND(SUM(purchase_amount), 2)    AS total_revenue
FROM customer
WHERE shipping_type IN ('Standard', 'Express')
GROUP BY shipping_type
ORDER BY avg_spend DESC;


-- =============================================================================
-- QUERY 5: Subscriber vs Non-Subscriber Metrics
-- Business Question: Do subscribers spend more and generate more revenue than
--                    non-subscribers?
-- Why useful: Quantifies the financial lift of the subscription programme —
--             key input for deciding subscription pricing and retention spend.
-- =============================================================================
SELECT
    CASE subscription_status
        WHEN 1 THEN 'Subscriber'
        WHEN 0 THEN 'Non-Subscriber'
    END                               AS subscriber_label,
    COUNT(*)                          AS customer_count,
    ROUND(AVG(purchase_amount), 2)    AS avg_spend,
    ROUND(SUM(purchase_amount), 2)    AS total_revenue,
    ROUND(
        100.0 * SUM(purchase_amount)
        / SUM(SUM(purchase_amount)) OVER (),
        1
    )                                 AS revenue_share_pct
FROM customer
GROUP BY subscription_status
ORDER BY subscription_status DESC;   -- Subscribers (1) first
