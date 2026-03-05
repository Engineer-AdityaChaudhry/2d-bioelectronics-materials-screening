.PHONY: all small big expanded prefilter layered rank loc stacks multiphysics stackcards viz reports clean clean_cache help

# -------------------------
# Defaults
# -------------------------
all: big stacks multiphysics stackcards viz reports

help:
	@echo "Targets:"
	@echo "  make all            - run the full BIG pipeline + stacks + multiphysics + reports + viz"
	@echo "  make big            - expanded fetch -> prefilter -> layered -> rank -> loc (BIG dataset)"
	@echo "  make small          - small/seed pipeline (if you still use mp_fetch_candidates.py etc.)"
	@echo "  make stacks         - heterostructure stack simulation (Module 10)"
	@echo "  make multiphysics   - multiphysics classification (Module 11)"
	@echo "  make stackcards     - generate stack cards markdown + csv"
	@echo "  make viz            - generate figures"
	@echo "  make clean          - remove processed outputs (keeps raw + external + cache)"
	@echo "  make clean_cache    - remove cached structures/partials"
	@echo ""
	@echo "Notes:"
	@echo "  - Uses your existing folder structure under data/, reports/, figures/, src/."

# -------------------------
# Core BIG pipeline (recommended)
# -------------------------
big: expanded prefilter layered rank loc

expanded:
	python src/fetch/mp_fetch_expanded.py

prefilter:
	python src/featurize/prefilter_layered_chemistry.py

layered:
	python src/featurize/layeredness_score_cached.py

rank:
	python src/featurize/add_layered_continuous_metrics_big.py
	python src/rank/rank_big_baseline_v3.py

loc:
	python src/featurize/loc_ooc_scores_big_v3.py

# -------------------------
# Optional SMALL pipeline (if you still keep/use these scripts)
# -------------------------
small:
	python src/fetch/mp_fetch_candidates.py
	python src/featurize/filter_semiconductors.py
	python src/featurize/layeredness_score_v2.py
	python src/featurize/add_layered_continuous_metrics.py
	python src/rank/rank_baseline_pareto_v3.py
	python src/featurize/loc_ooc_scores_v3.py
	python src/featurize/integration_stack_tags.py

# -------------------------
# External + Module 10/11
# -------------------------
# (You already have data/external/2dmatpedia_props.csv; this target just re-parses if needed.)
external:
	python src/external/parse_2dmatpedia.py

stacks: external
	python src/stack/heterostack_sim.py

multiphysics: external
	python src/featurize/multiphysics_classify.py

# -------------------------
# Reports
# -------------------------
stackcards:
	python src/reports/make_stack_cards.py

reports: stacks multiphysics stackcards
	@echo "Reports generated in ./reports"

# -------------------------
# Visualization (figures/)
# -------------------------
viz:
	python src/viz/plot_pareto_baseline.py
	python src/viz/plot_rank_shift.py
	python src/viz/plot_rank_shift_v2.py

# -------------------------
# Cleanup
# -------------------------
clean:
	rm -rf data/processed/*
	rm -rf reports/*
	rm -rf figures/*

clean_cache:
	rm -rf data/cache/partials/*
	rm -rf data/cache/structures/*

.PHONY: selected

selected:
	python src/reports/selected_materials_summary.py