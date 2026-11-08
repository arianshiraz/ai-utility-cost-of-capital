# Figures for H1 and H2 (tidyplots + ggdist). Run from the repository root after the Python stages:
#   Rscript code/16_figures.R
# Each figure is written as PDF (paper) and PNG (README).

suppressPackageStartupMessages({
  library(readr); library(dplyr); library(tidyr)
  library(ggplot2); library(tidyplots); library(ggdist); library(distributional)
})

tab <- function(f) read_csv(file.path("output", "tables", f), show_col_types = FALSE)
fig <- file.path("output", "figures")
dir.create(fig, showWarnings = FALSE, recursive = TRUE)
okabe <- as.vector(unclass(colors_discrete_okabeito))
names(okabe) <- NULL
save_both <- function(p, name, width, height) {
  for (ext in c("pdf", "png")) {
    ggsave(file.path(fig, paste0(name, ".", ext)), p, width = width, height = height,
           units = "mm", dpi = 300, bg = "white")
  }
}

# Figure 1. H1: change in AI beta against FY2023 data-centre exposure, US regulated electric utilities.
u <- tab("h1_utility_betas.csv")
ex <- tab("dc_exposure_candidates.csv") |> filter(vintage == "FY2023") |> select(ticker, mentions_per_10k)
us <- u |> filter(country == "US", role == "regulated_electric") |> inner_join(ex, by = "ticker")
p1 <- us |>
  tidyplot(x = mentions_per_10k, y = d_b_ai) |>
  add_data_points(color = okabe[2], size = 1.6, alpha = 0.8) |>
  add_curve_fit(method = "lm", color = okabe[6], fill = okabe[6], alpha = 0.15) |>
  add_reference_lines(y = 0) |>
  adjust_x_axis_title("Data-centre mentions per 10,000 words, FY2023 10-K") |>
  adjust_y_axis_title("Change in AI beta (AI era minus pre-AI)") |>
  adjust_font(fontsize = 8) |>
  adjust_size(width = 90, height = 60, unit = "mm")
save_both(p1, "fig1_h1_exposure_scatter", 110, 80)

# Figure 2. H1: AI-era exposure slope against the distribution of 1,000 placebo-break slopes.
pb <- tab("h1_placebo_breaks.csv")
main <- tab("h1_tests.csv") |> filter(grepl("^main", test)) |> pull(slope)
p2 <- ggplot(pb, aes(x = slope, y = 0)) +
  stat_halfeye(fill = okabe[2], alpha = 0.7, .width = c(0.66, 0.95), point_interval = median_qi) +
  geom_vline(xintercept = main, colour = okabe[6], linewidth = 0.8) +
  annotate("text", x = main, y = 0.55, label = "AI-era slope", colour = okabe[6], hjust = -0.08, size = 2.8) +
  labs(x = "Slope of the change in AI beta on exposure (1,000 placebo break dates, 2015 to 2021)", y = NULL) +
  theme_classic(base_size = 8) +
  theme(axis.text.y = element_blank(), axis.ticks.y = element_blank())
save_both(p2, "fig2_h1_placebo_breaks", 110, 70)

# Figure 3. H2: decomposition of the change in regulator-style beta, main windows, country means.
cn <- tab("h2_country.csv") |>
  filter(main_window | country == "CA") |>
  mutate(label = paste0(country, " (", window_years, "y ", frequency, ", n=", n_utilities, ")")) |>
  select(label, d_beta, exposure_term, non_ai_term, composition_term) |>
  pivot_longer(c(exposure_term, non_ai_term, composition_term), names_to = "term", values_to = "value") |>
  mutate(term = factor(term, levels = c("exposure_term", "non_ai_term", "composition_term"),
                       labels = c("Exposure (covariance with AI part of index)",
                                  "Non-AI (covariance with rest of index)",
                                  "Index variance (labelled composition)")))
nets <- cn |> distinct(label, d_beta)
p3 <- ggplot(cn, aes(x = value, y = label, fill = term)) +
  geom_col(width = 0.6) +
  geom_point(data = nets, aes(x = d_beta, y = label), inherit.aes = FALSE, shape = 23, size = 2.2,
             fill = "white", colour = "black") +
  geom_vline(xintercept = 0, linewidth = 0.3) +
  scale_fill_manual(values = okabe[c(6, 2, 3)]) +
  labs(x = "Change in beta, 2022 window to 2026 window (diamond: net change)", y = NULL, fill = NULL) +
  theme_classic(base_size = 8) +
  theme(legend.position = "bottom", legend.direction = "vertical")
save_both(p3, "fig3_h2_decomposition", 150, 95)
cat("figures written\n")
