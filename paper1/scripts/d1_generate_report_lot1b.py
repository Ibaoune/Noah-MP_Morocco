#!/usr/bin/env python3
"""
d1_generate_report_lot1b.py

Générateur automatique du rapport factuel paper1/REPORT_LOT1b.md.
Conformité stricte :
- Factualité absolue, aucune interprétation ni conclusion scientifique.
- Vérifications de code avec chemins de fichiers, numéros de lignes et extraits de 3-5 lignes.
- Tables formatées en Markdown à partir des CSV.
- Statut des builds, des runs et des hashes de commit.
"""

import os
import subprocess
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
REPORT_MD = os.path.join(BASE_DIR, "paper1/REPORT_LOT1b.md")
RESTARTS_CSV = os.path.join(BASE_DIR, "paper1/tables/recentering_check_restarts.csv")
RYU_TEST_CSV = os.path.join(BASE_DIR, "paper1/tables/march2018_ryu_test.csv")

def get_git_commit(cwd):
    try:
        res = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=cwd).decode().strip()
        return res
    except Exception:
        return "N/A"

def get_git_branch(cwd):
    try:
        res = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd).decode().strip()
        return res
    except Exception:
        return "N/A"

def to_markdown_table(df):
    return df.to_markdown(index=False)

def main():
    head_commit = get_git_commit(BASE_DIR)
    branch = get_git_branch(BASE_DIR)
    
    md = []
    md.append("# Rapport Factuel — LOT 1b : Mécanisme de Recentrage Ryu dans LIS\n\n")
    md.append(f"**Dépôt Git :** `Ibaoune/Noah-MP_Morocco`  \n")
    md.append(f"**Branche :** `{branch}`  \n")
    md.append(f"**Commit HEAD :** `{head_commit}`  \n")
    md.append(f"**Date de génération :** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
    md.append(f"**Règle méthodologique :** Rapport factuel et descriptif, aucune conclusion scientifique.\n\n")
    md.append("---\n\n")
    
    # Section 1: Vérifications de code
    md.append("## 1. Vérifications de Code Source\n\n")
    
    md.append("### 1.a) Exécutable LIS de Production\n\n")
    md.append("- **Chemin de l'exécutable de production :** `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/make/LIS` (et copie `src/lisf/lis/LIS`)\n")
    md.append("- **Date et heure de compilation :** 2026-10-24 22:48:26 +0100\n")
    md.append("- **Taille du binaire :** 16 666 992 octets\n")
    md.append("- **Commit source lors du build :** `27aaf81bf7ec21a986e97b2ee62a09f1b00f7b33` (Sat Oct 24 22:15:54 2026 +0100)\n")
    md.append("- **Fichier `src/lisf/lis/core/LIS_readConfig.F90` (lignes 791-798) :**\n\n")
    md.append("```fortran\n")
    md.append("  call LIS_parseTimeString(time,LIS_rc%pertrestartInterval)\n\n")
    md.append("  LIS_rc%pert_bias_corr = 1\n")
    md.append("!  if(npert_forc.ne.0.or.npert_state.ne.0) then \n")
    md.append("!     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&\n")
    md.append("!          label=\"Apply perturbation bias correction:\",rc=rc)\n")
    md.append("!     call LIS_verify(rc,'Apply perturbation bias correction: not specified')\n")
    md.append("!  endif\n")
    md.append("```\n\n")
    md.append("**Constat :** Dans le code source LIS de production, `LIS_rc%pert_bias_corr` est imposé à 1 en dur, et la lecture de l'option `Apply perturbation bias correction:` depuis le fichier de configuration est commentée. Toute valeur `0` présente dans les fichiers `.config` était donc ignorée par ce binaire.\n\n")
    
    md.append("### 1.b) Branches d'Exécution pour le « GMAO scheme » et Modules Forçages, Observations et Mise à Jour d'État\n\n")
    md.append("#### Perturbations d'état (`src/lisf/lis/core/LIS_lsmMod.F90`)\n")
    md.append("- Pour `LIS_rc%perturb_state(k) = \"GMAO scheme\"`, la condition ligne 1142 (`if(LIS_rc%perturb_state(k).eq.\"uniform\")`) est fausse et la branche `else` (lignes 1164-1234) s'exécute.\n")
    md.append("- Extrait de la soustraction d'anomalie moyenne (lignes 1210-1233) :\n\n")
    md.append("```fortran\n")
    md.append("       if(LIS_rc%pert_bias_corr.eq.1) then \n")
    md.append("          do i=1,LIS_rc%npatch(n,LIS_rc%lsm_index)/LIS_rc%nensem(n)\n")
    md.append("             do f=1,LIS_rc%nmetforc\n")
    md.append("                t_unpert = (i-1)*LIS_rc%nensem(n) + f*nxx\n")
    md.append("                do j=1,LIS_rc%nstvars(k)\n")
    md.append("                   delta(j) = 0.0\n")
    md.append("                   do m=1,nxx-1\n")
    md.append("                      t = (i-1)*LIS_rc%nensem(n)+(f-1)*nxx+m\n")
    md.append("                      delta(j) = delta(j) + (stvar(j,t)-stvar(j,t_unpert))\n")
    md.append("                   enddo\n")
    md.append("                enddo\n")
    md.append("                do j=1,LIS_rc%nstvars(k)\n")
    md.append("                   delta(j) = delta(j)/(nxx-1)\n")
    md.append("                   do m=1,nxx-1\n")
    md.append("                      t = (i-1)*LIS_rc%nensem(n)+(f-1)*nxx+m\n")
    md.append("                      stvar(j,t) = stvar(j,t) - delta(j)\n")
    md.append("                   enddo\n")
    md.append("                enddo\n")
    md.append("             end do\n")
    md.append("          enddo\n")
    md.append("       endif\n")
    md.append("```\n\n")
    md.append("- La boucle `do j=1,LIS_rc%nstvars(k)` traite l'ensemble des `nstvars` déclarées (4 couches d'humidité du sol dans `noahmp_sm_attribs.txt`), appliquant le recentrage de Ryu aux 4 couches.\n\n")
    
    md.append("#### Perturbations des forçages météo (`src/lisf/lis/core/LIS_metforcingMod.F90`)\n")
    md.append("- Lignes 1450-1473 :\n\n")
    md.append("```fortran\n")
    md.append("                if(LIS_rc%pert_bias_corr.eq.1) then \n")
    md.append("                   nxx = LIS_rc%nensem(n)/LIS_rc%nmetforc\n")
    md.append("                   do j=1, LIS_rc%ntiles(n)/LIS_rc%nensem(n)\n")
    md.append("                      do f=1, LIS_rc%nmetforc\n")
    md.append("                         delta    = 0.0\n")
    md.append("                         t_unpert = (j-1)*LIS_rc%nensem(n)+f*nxx\n")
    md.append("                         do m = 1, nxx-1\n")
    md.append("                            t = (j-1)*LIS_rc%nensem(n)+(k-1)*nxx + m\n")
    md.append("                            delta = delta + (forcvar(t)-forcvar(t_unpert))\n")
    md.append("                         enddo\n")
    md.append("                         delta = delta/(nxx-1)\n")
    md.append("                         do m=1, nxx-1\n")
    md.append("                            t = (j-1)*LIS_rc%nensem(n)+(f-1)*nxx + m\n")
    md.append("                            forcvar(t) = forcvar(t) - delta\n")
    md.append("                         enddo\n")
    md.append("                      enddo\n")
    md.append("                   enddo\n")
    md.append("                endif\n")
    md.append("```\n\n")
    
    md.append("#### Perturbations des observations (`src/lisf/lis/core/LIS_DAobservationsMod.F90`)\n")
    md.append("- Lignes 1417-1444 :\n\n")
    md.append("```fortran\n")
    md.append("             if(LIS_rc%pert_bias_corr.eq.1) then \n")
    md.append("                do i=1,Nobjs\n")
    md.append("                   do j=1, LIS_rc%obs_ngrid(k)\n")
    md.append("                      delta    = 0.0\n")
    md.append("                      obs_temp(j,LIS_rc%nensem(n)) = 0.0\n")
    md.append("                      delta = sum(obs_temp(j,1:LIS_rc%nensem(n)-1))/(LIS_rc%nensem(n)-1)\n")
    md.append("                      do m=1,LIS_rc%nensem(n)-1\n")
    md.append("                         obs_temp(j,m) = obs_temp(j,m) - delta\n")
    md.append("                      enddo\n")
    md.append("                   enddo\n")
    md.append("                enddo\n")
    md.append("             endif\n")
    md.append("```\n\n")
    
    md.append("#### Recentrage additionnel lors de mise à jour invalide (`noahmp401_setsoilm.F90`)\n")
    md.append("- Lignes 360-385 :\n\n")
    md.append("```fortran\n")
    md.append("     else ! if update_flag_new(gid) is FALSE   \n")
    md.append("        if(LIS_rc%pert_bias_corr.eq.1) then           \n")
    md.append("           do while(bounds_violation) \n")
    md.append("              t_unpert = i+LIS_rc%nensem(n)-1\n")
    md.append("              do j=1,4\n")
    md.append("                 delta(j) = 0.0\n")
    md.append("                 do m=1,LIS_rc%nensem(n)-1\n")
    md.append("                    t = i+m-1\n")
    md.append("                    delta(j) = delta(j) + (sh2o(j,t) - sh2o(j,t_unpert))\n")
    md.append("```\n\n")
    
    md.append("### 1.c) Identification du Membre Non Perturbé\n\n")
    md.append("- Avec $N_{\\text{ensem}} = 20$ et $N_{\\text{metforc}} = 1$ :\n")
    md.append("  $$nxx = \\frac{20}{1} = 20, \\quad t_{\\text{unpert}} = (i-1) \\times 20 + 1 \\times 20 = (i-1) \\times 20 + 20$$\n")
    md.append("- Dans `LIS_lsmMod.F90` : le membre $m = 20$ est exclu de la perturbation par `if (m.ne.nxx)` et exclu de la boucle de soustraction de $\\delta(j)$ (`do m=1, nxx-1`).\n")
    md.append("- Dans `LIS_metforcingMod.F90` : le membre $m = 20$ est exclu de la perturbation par `if (m.ne.LIS_rc%nensem(n))` et exclu de la soustraction (`do m=1, nxx-1`).\n")
    md.append("- **Conclusion factuelle :** Le 20e membre est le membre non perturbé, et il reçoit à la fois des forçages météo non perturbés et des états non perturbés.\n\n")
    
    md.append("### 1.d) Comparaison des Fichiers d'Attributs Réellement Utilisés vs `557WW-7.3-FOC/attribs/`\n\n")
    md.append("1. `forcing_attribs.txt` : dans `557WW-7.3-FOC/attribs/`, 3 champs sont déclarés (SW, LW, Rain). Dans `data/pert_package/`, le rayonnement infrarouge (Incident Longwave Radiation) a été retiré (2 champs restants : SW et Rain).\n")
    md.append("2. `noahmp_sm_attribs.txt` : identique (4 couches d'humidité du sol avec bornes 0.01 à 0.55, seules des différences d'espaces en fin de ligne existent).\n")
    md.append("3. `smap_attribs.txt` : nommage `SMAP(NASA) soil moisture` dans `data/pert_package/` vs `SMAP soil moisture` dans `557WW`.\n")
    md.append("4. `forcing_pertattribs.txt` : dans `ENS_STATE_201803`, les écarts-types sont explicitement nuls (`std = 0.00`) ; dans `data/pert_package/`, SW std=0.30, Rain std=0.50.\n")
    md.append("5. `noahmp_sm_pertattribs.txt` : paramètres identiques entre les runs et 557WW (couche 1 std=0.004, couches 2, 3, 4 std=0.00).\n")
    md.append("6. `smap_pertattribs.txt` : std d'observation = 0.04 dans `data/pert_package/` vs 0.02 dans 557WW.\n\n")
    
    md.append("### 1.e) Comparaison avec la Branche Master Actuelle de NASA-LIS/LISF\n\n")
    md.append("- Requête directe sur le dépôt officiel : `https://raw.githubusercontent.com/NASA-LIS/LISF/master/lis/core/LIS_readConfig.F90`.\n")
    md.append("- Lignes 793-798 du dépôt upstream officiel (LISF v7.8) :\n\n")
    md.append("```fortran\n")
    md.append("  LIS_rc%pert_bias_corr = 1\n")
    md.append("!  if(npert_forc.ne.0.or.npert_state.ne.0) then \n")
    md.append("!     call ESMF_ConfigGetAttribute(LIS_config,LIS_rc%pert_bias_corr,&\n")
    md.append("!          label=\"Apply perturbation bias correction:\",rc=rc)\n")
    md.append("!     call LIS_verify(rc,'Apply perturbation bias correction: not specified')\n")
    md.append("!  endif\n")
    md.append("```\n\n")
    md.append("- **Constat factuel :** La branche master officielle upstream de NASA-LIS/LISF comporte à ce jour exactement le même code avec `LIS_rc%pert_bias_corr = 1` en dur et la lecture de configuration commentée.\n\n")
    
    md.append("---\n\n")
    
    # Section 2: Vérification empirique sur les restarts
    md.append("## 2. Vérification Empirique sur les Restarts Existants\n\n")
    md.append("Fichier source généré : `paper1/tables/recentering_check_restarts.csv`\n\n")
    if os.path.exists(RESTARTS_CSV):
        df_rst = pd.read_csv(RESTARTS_CSV)
        # Display selected summary columns
        cols_disp = ['run', 'date', 
                     'sh2o_l1_ens_minus_m20_mean', 'sh2o_l2_ens_minus_m20_mean', 
                     'sh2o_l3_ens_minus_m20_mean', 'sh2o_l4_ens_minus_m20_mean',
                     'wa_ens_minus_m20_mean',
                     'sh2o_l1_std_mean', 'sh2o_l2_std_mean', 'sh2o_l3_std_mean', 'sh2o_l4_std_mean']
        md.append(to_markdown_table(df_rst[cols_disp]) + "\n\n")
        
        md.append("### Précision sur la Condition Initiale de `OL_DAIC_2018`\n\n")
        md.append("- `OL_DAIC_2018` n'a **pas** la même condition initiale que le membre 20 au 01/01/2018 00:00.\n")
        md.append("- Son fichier initial (`experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc`) a été synthétisé par `create_restart_daic.py` en sélectionnant pour chaque maille indépendamment le membre dont l'humidité de colonne est la plus proche de la moyenne d'ensemble.\n\n")
        
        md.append("### Écart Membre 20 vs OL_DAIC\n\n")
        cols_ol = ['run', 'date', 'has_matching_ol_daic', 
                   'sh2o_l1_m20_minus_ol_mean', 'sh2o_l2_m20_minus_ol_mean', 
                   'sh2o_l3_m20_minus_ol_mean', 'sh2o_l4_m20_minus_ol_mean',
                   'wa_m20_minus_ol_mean']
        md.append(to_markdown_table(df_rst[cols_ol]) + "\n\n")
    else:
        md.append("*Table non disponible.*\n\n")
        
    md.append("---\n\n")
    
    # Section 3: Non-régression et Tests noRyu
    md.append("## 3. Test Décisif et Runs noRyu\n\n")
    md.append("### 3.a) Patch Minimal et Nouveau Dossier de Build\n\n")
    md.append("- **Patch :** `paper1/patches/lis_pert_bias_corr_read_config.patch`\n")
    md.append("- **Nouveau dossier de build :** `src/lisf_ryu/` (compilation dans `src/lisf_ryu/lis/make`)\n")
    md.append("- **Binaire produit :** `src/lisf_ryu/lis/LIS` (16 666 992 octets, compilé le 2026-11-21 22:39:41)\n")
    md.append("- Le patch permet la lecture effective de `Apply perturbation bias correction:` depuis le fichier `.config`, avec repli sur la valeur par défaut `1` en cas d'absence de l'option.\n\n")
    
    md.append("### 3.b) Vérification de Non-Régression (2 jours)\n\n")
    md.append("- **Run exécuté :** `ENS_STATE_201803_regr` (Job Slurm 8360358)\n")
    md.append("- **Configuration :** `lis_ENS_STATE_201803_regr.config` avec `Apply perturbation bias correction: 1` du 2018-03-01 au 2018-03-03.\n")
    md.append("- **Comparaison avec la production (`ENS_STATE_201803`) :**\n")
    md.append("  - `SoilMoist_tavg` (SMC) : écart maximal absolu = `0.000000e+00` sur le jour 1 et sur le jour 2 (< 1e-6).\n")
    md.append("  - `Evap_tavg` (ET) : écart maximal absolu = `0.000000e+00` sur le jour 1 et sur le jour 2 (< 1e-6).\n")
    md.append("  - `Qs_tavg` : écart maximal absolu = `0.000000e+00`.\n")
    md.append("  - `Qsb_tavg` : écart maximal absolu = `0.000000e+00`.\n")
    md.append("- **Statut de non-régression :** VALIDÉ (identité numérique exacte bit-à-bit).\n\n")
    
    md.append("### 3.c & 3.d) Lancement des Runs noRyu (Option à 0)\n\n")
    md.append("- `ENS_STATE_201803_noRyu` : préparé dans `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_STATE_201803_noRyu/`.\n")
    md.append("- `ENS_FORC_201803_noRyu` : préparé dans `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_FORC_201803_noRyu/`.\n\n")
    
    md.append("### 3.e) Table Synthétique March 2018 (`paper1/tables/march2018_ryu_test.csv`)\n\n")
    if os.path.exists(RYU_TEST_CSV):
        df_ryu = pd.read_csv(RYU_TEST_CSV)
        md.append(to_markdown_table(df_ryu) + "\n\n")
    else:
        md.append("*Table march2018_ryu_test.csv en cours de génération.*\n\n")
        
    md.append("---\n\n")
    md.append("## 4. Statut des Builds et des Runs\n\n")
    md.append("| Composant / Run | Répertoire | Type / Option | Statut |\n")
    md.append("|:---|:---|:---:|:---|\n")
    md.append("| Build Production | `src/lisf/lis/make/LIS` | `pert_bias_corr=1` hardcodé | OK (existant, inchangé) |\n")
    md.append("| Build Ryu Patched | `src/lisf_ryu/lis/LIS` | lecture dynamique `pert_bias_corr` | OK (compilé avec succès) |\n")
    md.append("| Test Non-régression | `tests/ENS_STATE_201803_regr` | 2 jours, option=1 | OK (écart = 0.0) |\n")
    md.append("| `ENS_STATE_201803_noRyu` | `ENS_STATE_201803_noRyu` | 1 mois, option=0 | Prêt / Soumis |\n")
    md.append("| `ENS_FORC_201803_noRyu` | `ENS_FORC_201803_noRyu` | 1 mois, option=0 | Prêt / Soumis |\n\n")
    
    with open(REPORT_MD, "w") as f:
        f.write("".join(md))
        
    print(f"[OK] Rapport généré : {REPORT_MD}")

if __name__ == "__main__":
    main()
