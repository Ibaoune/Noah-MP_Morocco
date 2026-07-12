#!/usr/bin/env python3
import os
import argparse
import yaml
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

POSTPROC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(POSTPROC_DIR))

from src.lis_postproc.core.capabilities import DiagnosticCapability, DataCapabilityStatus, ImplementationStatus
from tools.audit.run_qc_real_data import run_qc

CONFIG_DIR = POSTPROC_DIR / "configs"
OUTPUTS_DIR = POSTPROC_DIR / "outputs" / "matrix_2016" / "opl_vs_smap_da_scientific"

# Load the baseline manifest to find protected paths
MANIFEST_PATH = POSTPROC_DIR / "outputs" / "matrix_2016" / "opl_vs_smap_da_scientific" / "provenance" / "baseline_manifest.yaml"

def load_yaml(filepath):
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def get_protected_paths():
    protected = []
    # Explicitly protect the exact baseline folder as requested
    explicit_baseline = POSTPROC_DIR / "outputs" / "matrix_2016" / "figures" / "smap_cdf_sensitivity"
    protected.append(explicit_baseline.resolve())
    
    if MANIFEST_PATH.exists():
        manifest = load_yaml(MANIFEST_PATH)
        prot_dir = manifest.get("protection", {}).get("protected_output_dir")
        if prot_dir:
            p = (POSTPROC_DIR / prot_dir).resolve()
            if p not in protected:
                protected.append(p)
    return protected

def is_protected(path: Path, protected_paths: list) -> bool:
    target = path.resolve()
    for p in protected_paths:
        if str(target).startswith(str(p)):
            return True
    return False

def evaluate_diagnostics(recipe):
    # Dummy capability registry for LOT 2B
    diags = recipe.get("diagnostics", {})
    plan = []
    
    # We define what is implemented in LOT 2B
    implemented_status = {
        "quality_control": ImplementationStatus.REAL_DATA_TESTED,
        "temporal_means": ImplementationStatus.NOT_IMPLEMENTED,
        "external_validation": ImplementationStatus.NOT_IMPLEMENTED,
        "water_balance": ImplementationStatus.NOT_IMPLEMENTED,
        "vertical_propagation": ImplementationStatus.NOT_IMPLEMENTED,
        "response_to_updates": ImplementationStatus.NOT_IMPLEMENTED,
        "drought_percentiles": ImplementationStatus.NOT_IMPLEMENTED,
    }
    
    data_status = {
        "quality_control": DataCapabilityStatus.READY,
        "temporal_means": DataCapabilityStatus.READY,
        "external_validation": DataCapabilityStatus.SKIPPED,
        "water_balance": DataCapabilityStatus.PARTIAL,
        "vertical_propagation": DataCapabilityStatus.PARTIAL,
        "response_to_updates": DataCapabilityStatus.PARTIAL,
        "drought_percentiles": DataCapabilityStatus.SKIPPED,
    }
    
    justifications = {
        "quality_control": "Ready and tested.",
        "temporal_means": "Module not implemented yet.",
        "external_validation": "WaPOR v2 2016 data missing.",
        "water_balance": "Water balance closure not implemented.",
        "vertical_propagation": "Increment sign/conversion not validated.",
        "response_to_updates": "Not fully implemented.",
        "drought_percentiles": "Climatology absent."
    }
    
    for diag_name, diag_cfg in diags.items():
        requested = diag_cfg.get("enabled", False)
        
        impl = implemented_status.get(diag_name, ImplementationStatus.NOT_IMPLEMENTED)
        data = data_status.get(diag_name, DataCapabilityStatus.SKIPPED)
        
        cap = DiagnosticCapability(
            name=diag_name,
            implementation_status=impl,
            data_status=data,
            missing_requirements=[]
        )
        
        decision = "EXECUTE" if requested and cap.can_run() else "SKIP"
        if not requested:
            decision = "IGNORED"
            
        plan.append({
            "diagnostic": diag_name,
            "requested": requested,
            "implementation_status": cap.implementation_status.value,
            "data_capability_status": cap.data_status.value,
            "decision": decision,
            "justification": justifications.get(diag_name, "N/A"),
            "missing_dependencies": "",
            "action_required": "Implement module" if decision == "SKIP" else "None"
        })
        
    return plan

def main():
    parser = argparse.ArgumentParser(description="Scientific Post-Processing Runner")
    parser.add_argument("--recipe", required=True, help="Path to YAML recipe")
    parser.add_argument("--dry-run", action="store_true", help="Print execution plan without running")
    parser.add_argument("--check-config", action="store_true", help="Validate recipe against experiments.yaml")
    parser.add_argument("--list-diagnostics", action="store_true", help="List available diagnostics")
    parser.add_argument("--show-capabilities", action="store_true", help="Show diagnostic capabilities")
    parser.add_argument("--make-products", action="store_true", help="Run actual diagnostic data generation")
    parser.add_argument("--make-figures", action="store_true", help="Run plotting")
    parser.add_argument("--make-report", action="store_true", help="Generate final report")
    
    args = parser.parse_args()
    
    recipe_path = Path(args.recipe)
    if not recipe_path.exists():
        print(f"ERROR: Recipe not found at {recipe_path}")
        sys.exit(1)
        
    try:
        recipe = load_yaml(recipe_path)
    except Exception as e:
        print(f"ERROR: Invalid YAML in recipe: {e}")
        sys.exit(1)

    # Validate against experiments.yaml
    exp_yaml = CONFIG_DIR / "experiments.yaml"
    if exp_yaml.exists():
        catalog = load_yaml(exp_yaml)
        valid_ids = list(catalog.get("experiments", {}).keys())
        
        ref = recipe.get("experiments", {}).get("reference")
        cands = recipe.get("experiments", {}).get("candidates", [])
        
        if ref not in valid_ids:
            print(f"ERROR: Reference experiment ID '{ref}' not found in experiments.yaml")
            sys.exit(1)
            
        for c in cands:
            if c not in valid_ids:
                print(f"ERROR: Candidate experiment ID '{c}' not found in experiments.yaml")
                sys.exit(1)
                
        # Also validate comparisons
        comps = recipe.get("comparisons", [])
        comp_ids = set()
        for comp in comps:
            if comp.get("reference") == comp.get("candidate"):
                print("ERROR: Comparison reference and candidate cannot be the same.")
                sys.exit(1)
            cid = comp.get("comparison_id")
            if cid in comp_ids:
                print(f"ERROR: Duplicate comparison_id '{cid}'")
                sys.exit(1)
            comp_ids.add(cid)

    # Protect baseline
    protected = get_protected_paths()
    if is_protected(OUTPUTS_DIR, protected):
        print(f"ERROR: Output directory {OUTPUTS_DIR} resolves to a protected baseline path!")
        sys.exit(1)
        
    plan = evaluate_diagnostics(recipe)
    
    is_dry_run = args.dry_run or not (args.make_products or args.make_figures or args.make_report)
    
    if args.list_diagnostics:
        print("Available diagnostics:")
        print("- quality_control")
        print("- temporal_means")
        print("- external_validation")
        print("- water_balance")
        print("- vertical_propagation")
        print("- response_to_updates")
        print("- drought_percentiles")
        
    if args.show_capabilities:
        print("Diagnostic Capabilities Status:")
        df = pd.DataFrame(plan)
        if not df.empty:
            print(df[['diagnostic', 'implementation_status', 'data_capability_status']].to_string(index=False))
        else:
            print("No diagnostics evaluated in the current recipe.")
            
    if args.check_config:
        print("Config checked successfully.")
        
    if is_dry_run:
        print("=== DRY RUN PLAN ===")
        print(f"Recipe: {recipe.get('recipe_id')}")
        print(f"Period: {recipe.get('analysis_period')}")
        print("Resolved Outputs Dir:", OUTPUTS_DIR.resolve())
        print("Diagnostics Plan:")
        df = pd.DataFrame(plan)
        print(df.to_string())
        print("Baseline protected paths checked.")
        print("=== END DRY RUN ===")
        
    else:
        print("Creating output hierarchy...")
        for sub in ["intermediate", "metrics", "tables", "figures", "provenance", "logs", "pdf"]:
            (OUTPUTS_DIR / sub).mkdir(parents=True, exist_ok=True)
            
        prov_dir = OUTPUTS_DIR / "provenance"
        
        df = pd.DataFrame(plan)
        df.to_csv(prov_dir / "diagnostic_execution_plan.csv", index=False)
        
        with open(prov_dir / "resolved_recipe.yaml", "w") as f:
            yaml.dump(recipe, f, default_flow_style=False)
            
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "recipe_id": recipe.get("recipe_id"),
            "command": " ".join(sys.argv),
            "diagnostics_executed": [p["diagnostic"] for p in plan if p["decision"] == "EXECUTE"],
            "diagnostics_skipped": [p["diagnostic"] for p in plan if p["decision"] == "SKIP"],
        }
        with open(prov_dir / "scientific_run_manifest.yaml", "w") as f:
            yaml.dump(manifest, f, default_flow_style=False)
            
        for p in plan:
            if p["decision"] == "EXECUTE" and p["diagnostic"] == "quality_control":
                print("Executing Quality Control...")
                run_qc()
                
    if args.make_figures:
        print("Executing plotting routines...")
        print("Notice: 'quality_control' does not produce figures yet.")
        print("Notice: No other diagnostics are ready to plot.")
        
    if args.make_report:
        print("Generating final report...")
        print("Notice: No scientific data or figures generated yet to build a full report.")

if __name__ == "__main__":
    main()
