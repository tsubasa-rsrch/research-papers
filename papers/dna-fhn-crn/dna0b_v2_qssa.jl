########################################################################
# DNA-0b v2: FHN → CRN via QSSA Intermediate Species
#
# Previous result (v1): Quadratization route fails for long-time integration.
#   - Self-catalytic term 2q amplifies q-v² drift exponentially
#   - t=10: q_err=1e-10 (good), t=200: q_err=4310 (explosion)
#
# This version: QSSA route (Echo's original approach, refined)
#   - Cubic term v³ handled via intermediate species P ≈ v²
#   - P tracks v² via fast equilibrium (rate k_fast), not exact invariant
#   - Key advantage: P-v² drift is SUPPRESSED by k_fast, not AMPLIFIED
#
# Three-way comparison:
#   1. FHN reference (2 vars)
#   2. QSSA CRN (8 vars: v+,v-,w+,w-,P_pp,P_mm,P_pm + annihilation)
#   3. Quadratized CRN (6 vars, from v1 -- for negative result comparison)
########################################################################

using OrdinaryDiffEq
using Statistics
using Printf

# =====================================================================
# Parameters
# =====================================================================
Base.@kwdef struct FHNParams
    a::Float64 = 0.7
    b::Float64 = 0.8
    ε::Float64 = 0.08
    I::Float64 = 0.5
end

# =====================================================================
# 1. Reference FHN
# =====================================================================
function fhn_ode!(du, u, p::FHNParams, t)
    v, w = u
    du[1] = v - v^3/3 - w + p.I
    du[2] = p.ε * (v + p.a - p.b * w)
end

# =====================================================================
# 2. QSSA CRN Route
#
# Design principle:
#   - v³/3 = v * v² ≈ v * P  (where P tracks v² via fast reactions)
#   - P is maintained by: production at rate k_fast*v², decay at rate k_fast*P
#   - At QSSA: dP/dt ≈ 0 → P ≈ v²
#   - Crucially: if P drifts from v², the fast decay PULLS IT BACK
#     (unlike quadratization where drift is amplified)
#
# For dual-rail: v = v+ - v-, so v² = v+² - 2*v+*v- + v-²
#   P_pp tracks v+²  (via k_fast * v+ * v+ production, k_fast * P_pp decay)
#   P_mm tracks v-²  (via k_fast * v- * v- production, k_fast * P_mm decay)
#   P_pm tracks v+*v- (via k_fast * v+ * v- production, k_fast * P_pm decay)
#
# Then: v³ = (v+-v-)³ = (v+-v-)(v+²-2v+v-+v-²)
#      = (v+-v-)(P_pp - 2*P_pm + P_mm)
#      v*P_pp = v+*P_pp - v-*P_pp
#      v*P_mm = v+*P_mm - v-*P_mm  
#      v*P_pm = v+*P_pm - v-*P_pm
#
# So -v³/3 contributes terms like:
#   -(v+*P_pp - v-*P_pp - 2*v+*P_pm + 2*v-*P_pm + v+*P_mm - v-*P_mm)/3
#
# All bimolecular! No intermediate q variable with self-catalytic feedback.
#
# Species: v+, v-, w+, w-, P_pp, P_mm, P_pm  (7 species)
# =====================================================================

Base.@kwdef struct QSSAParams
    fhn::FHNParams = FHNParams()
    k_ann::Float64  = 100.0    # annihilation rate
    k_fast::Float64 = 1000.0   # QSSA timescale (P tracking speed)
end

function qssa_crn_ode!(du, u, p::QSSAParams, t)
    vp, vm, wp, wm, P_pp, P_mm, P_pm = u
    (; a, b, ε, I) = p.fhn
    k   = p.k_ann
    kf  = p.k_fast
    
    # Annihilation
    ann_v = k * vp * vm
    ann_w = k * wp * wm
    
    # --- QSSA intermediate species dynamics ---
    # P_pp tracks v+²:  production = kf * vp², decay = kf * P_pp
    # P_mm tracks v-²:  production = kf * vm², decay = kf * P_mm
    # P_pm tracks v+*v-: production = kf * vp*vm, decay = kf * P_pm
    #
    # dP_pp/dt = kf * (vp² - P_pp)
    # dP_mm/dt = kf * (vm² - P_mm)
    # dP_pm/dt = kf * (vp*vm - P_pm)
    #
    # At steady state: P_pp = vp², P_mm = vm², P_pm = vp*vm
    
    du[5] = kf * (vp^2 - P_pp)
    du[6] = kf * (vm^2 - P_mm)
    du[7] = kf * (vp * vm - P_pm)
    
    # --- Cubic term decomposition ---
    # v³/3 = v * v²/3 = (vp-vm)(vp²-2vp*vm+vm²)/3
    #       ≈ (vp-vm)(P_pp - 2*P_pm + P_mm)/3
    #
    # Expand: (vp-vm)(P_pp - 2P_pm + P_mm)/3
    #   = (vp*P_pp - vm*P_pp - 2vp*P_pm + 2vm*P_pm + vp*P_mm - vm*P_mm)/3
    #
    # For -v³/3, negate everything:
    # Positive contributions (go to dv+/dt):
    #   vm*P_pp/3 + 2*vp*P_pm/3 + vm*P_mm/3  ... wait
    #
    # Let me be very careful with signs.
    # -v³/3 = -(vp*P_pp - vm*P_pp - 2vp*P_pm + 2vm*P_pm + vp*P_mm - vm*P_mm)/3
    #
    # Term by term, each with its sign after the outer negation:
    #   -vp*P_pp/3    → negative → goes to dv-/dt as source
    #   +vm*P_pp/3    → positive → goes to dv+/dt as source
    #   +2vp*P_pm/3   → positive → goes to dv+/dt as source
    #   -2vm*P_pm/3   → negative → goes to dv-/dt as source
    #   -vp*P_mm/3    → negative → goes to dv-/dt as source
    #   +vm*P_mm/3    → positive → goes to dv+/dt as source
    
    cubic_to_vp = (vm*P_pp + 2*vp*P_pm + vm*P_mm) / 3
    cubic_to_vm = (vp*P_pp + 2*vm*P_pm + vp*P_mm) / 3
    
    # --- Main species dynamics ---
    
    # dv/dt = v - v³/3 - w + I
    # Positive parts → dv+/dt, negative parts → dv-/dt
    
    # dv+/dt:
    #   +vp (autocatalytic)
    #   +cubic_to_vp (cubic suppression, positive part)
    #   +wm (from -w)
    #   +I (external input)
    #   -ann_v (annihilation)
    du[1] = vp + cubic_to_vp + wm + I - ann_v
    
    # dv-/dt:
    #   +vm (autocatalytic)
    #   +cubic_to_vm (cubic suppression, negative part)
    #   +wp (from -w)
    #   -ann_v (annihilation)
    du[2] = vm + cubic_to_vm + wp - ann_v
    
    # dw/dt = ε(v + a - bw)
    du[3] = ε*(vp + a + b*wm) - ann_w    # dw+/dt
    du[4] = ε*(vm + b*wp) - ann_w          # dw-/dt
end

# =====================================================================
# 3. Quadratized CRN (from v1 -- for comparison)
# =====================================================================
Base.@kwdef struct QuadCRNParams
    fhn::FHNParams = FHNParams()
    k_ann::Float64 = 100.0
end

function quad_crn_ode!(du, u, p::QuadCRNParams, t)
    vp, vm, wp, wm, qp, qm = u
    (; a, b, ε, I) = p.fhn
    k = p.k_ann
    
    ann_v = k * vp * vm
    ann_w = k * wp * wm
    ann_q = k * qp * qm
    
    du[1] = vp + (qp*vm + qm*vp)/3 + wm + I - ann_v
    du[2] = vm + (qp*vp + qm*vm)/3 + wp - ann_v
    du[3] = ε*(vp + a + b*wm) - ann_w
    du[4] = ε*(vm + b*wp) - ann_w
    du[5] = 2*qp + (4/3)*qp*qm + 2*(vp*wm + vm*wp) + 2*I*vp - ann_q
    du[6] = 2*qm + (2/3)*(qp^2 + qm^2) + 2*(vp*wp + vm*wm) + 2*I*vm - ann_q
end

# =====================================================================
# Initial conditions
# =====================================================================
function fhn_to_qssa_ic(v0, w0)
    vp = max(v0, 0.0)
    vm = max(-v0, 0.0)
    wp = max(w0, 0.0)
    wm = max(-w0, 0.0)
    # QSSA intermediates at equilibrium
    P_pp = vp^2
    P_mm = vm^2
    P_pm = vp * vm
    return [vp, vm, wp, wm, P_pp, P_mm, P_pm]
end

function fhn_to_quad_ic(v0, w0)
    vp = max(v0, 0.0)
    vm = max(-v0, 0.0)
    wp = max(w0, 0.0)
    wm = max(-w0, 0.0)
    q0 = v0^2
    qp = max(q0, 0.0)
    qm = max(-q0, 0.0)
    return [vp, vm, wp, wm, qp, qm]
end

# =====================================================================
# Three-way comparison
# =====================================================================
function run_threeway(;
    p_fhn  = FHNParams(),
    k_ann  = 100.0,
    k_fast = 1000.0,
    tspan  = (0.0, 200.0),
    v0 = -1.0, w0 = -0.5,
    solver = Rodas5P(),
    abstol = 1e-10,
    reltol = 1e-8,
    saveat = 0.01
)
    # 1. FHN reference
    prob_fhn = ODEProblem(fhn_ode!, [v0, w0], tspan, p_fhn)
    sol_fhn = solve(prob_fhn, solver; abstol, reltol, saveat)
    
    # 2. QSSA CRN
    u0_qssa = fhn_to_qssa_ic(v0, w0)
    p_qssa = QSSAParams(fhn=p_fhn, k_ann=k_ann, k_fast=k_fast)
    prob_qssa = ODEProblem(qssa_crn_ode!, u0_qssa, tspan, p_qssa)
    sol_qssa = solve(prob_qssa, solver; abstol, reltol, saveat)
    
    # 3. Quadratized CRN (for negative result comparison)
    u0_quad = fhn_to_quad_ic(v0, w0)
    p_quad = QuadCRNParams(fhn=p_fhn, k_ann=k_ann)
    prob_quad = ODEProblem(quad_crn_ode!, u0_quad, tspan, p_quad)
    sol_quad = solve(prob_quad, solver; abstol, reltol, saveat)
    
    return sol_fhn, sol_qssa, sol_quad
end

function compute_threeway_metrics(sol_fhn, sol_qssa, sol_quad; skip=50.0)
    idx_fhn  = findall(t -> t >= skip, sol_fhn.t)
    idx_qssa = findall(t -> t >= skip, sol_qssa.t)
    idx_quad = findall(t -> t >= skip, sol_quad.t)
    
    # FHN reference
    v_fhn = [sol_fhn[1,i] for i in idx_fhn]
    
    # QSSA: extract v = v+ - v-, and check P_pp ≈ v+²
    v_qssa = [sol_qssa[1,i] - sol_qssa[2,i] for i in idx_qssa]
    vp_qssa = [sol_qssa[1,i] for i in idx_qssa]
    P_pp    = [sol_qssa[5,i] for i in idx_qssa]
    p_err_qssa = sqrt(mean((P_pp .- vp_qssa.^2).^2))  # P_pp tracking error
    
    # Quadratized: extract v = v+ - v-, check q ≈ v²
    v_quad = [sol_quad[1,i] - sol_quad[2,i] for i in idx_quad]
    v_quad_full = [sol_quad[1,i] - sol_quad[2,i] for i in idx_quad]
    q_quad = [sol_quad[5,i] - sol_quad[6,i] for i in idx_quad]
    q_err_quad = sqrt(mean((q_quad .- v_quad_full.^2).^2))
    
    # Trajectory RMSE vs FHN
    n_qssa = min(length(v_fhn), length(v_qssa))
    n_quad = min(length(v_fhn), length(v_quad))
    
    rmse_qssa = sqrt(mean((v_fhn[1:n_qssa] .- v_qssa[1:n_qssa]).^2))
    rmse_quad = sqrt(mean((v_fhn[1:n_quad] .- v_quad[1:n_quad]).^2))
    
    # Dual-rail drift
    drift_qssa = mean(min.([sol_qssa[1,i] for i in idx_qssa],
                           [sol_qssa[2,i] for i in idx_qssa]))
    drift_quad = mean(min.([sol_quad[1,i] for i in idx_quad],
                           [sol_quad[2,i] for i in idx_quad]))
    
    return (
        rmse_qssa     = rmse_qssa,
        rmse_quad     = rmse_quad,
        p_err_qssa    = p_err_qssa,    # P_pp - vp² (QSSA tracking)
        q_err_quad    = q_err_quad,    # q - v² (quadratization drift)
        drift_qssa    = drift_qssa,
        drift_quad    = drift_quad,
    )
end

# =====================================================================
# Sweep: k_fast (QSSA timescale) at fixed k_ann
# =====================================================================
function k_fast_sweep(;
    k_fast_values = [10.0, 50.0, 100.0, 500.0, 1000.0, 5000.0],
    k_ann = 100.0,
    tspan = (0.0, 200.0),
    p_fhn = FHNParams(),
    v0 = -1.0, w0 = -0.5
)
    println("=" ^ 80)
    println("DNA-0b v2: QSSA vs Quadratization comparison")
    println("k_ann = $k_ann (fixed), sweeping k_fast")
    println("FHN params: a=$(p_fhn.a), b=$(p_fhn.b), ε=$(p_fhn.ε), I=$(p_fhn.I)")
    println("=" ^ 80)
    @printf("%-10s | %-12s %-12s | %-14s %-14s | %-10s %-10s\n",
        "k_fast", "RMSE(QSSA)", "RMSE(Quad)", "P_err(QSSA)", "q_err(Quad)",
        "drift_Q", "drift_Qd")
    println("-" ^ 80)
    
    results = []
    for kf in k_fast_values
        try
            sol_fhn, sol_qssa, sol_quad = run_threeway(;
                p_fhn, k_ann, k_fast=kf, tspan, v0, w0
            )
            m = compute_threeway_metrics(sol_fhn, sol_qssa, sol_quad)
            @printf("%-10.0f | %-12.6f %-12.6f | %-14.2e %-14.2e | %-10.4f %-10.4f\n",
                kf, m.rmse_qssa, m.rmse_quad,
                m.p_err_qssa, m.q_err_quad,
                m.drift_qssa, m.drift_quad)
            push!(results, (k_fast=kf, m...))
        catch e
            @printf("%-10.0f | FAILED: %s\n", kf, string(e)[1:min(60, end)])
            push!(results, (k_fast=kf, rmse_qssa=NaN, rmse_quad=NaN,
                           p_err_qssa=NaN, q_err_quad=NaN,
                           drift_qssa=NaN, drift_quad=NaN))
        end
    end
    
    println("=" ^ 80)
    return results
end

# =====================================================================
# k_ann sweep at fixed k_fast (for QSSA route)
# =====================================================================
function k_ann_sweep_qssa(;
    k_ann_values = [10.0, 50.0, 100.0, 500.0, 1000.0],
    k_fast = 1000.0,
    tspan = (0.0, 200.0),
    p_fhn = FHNParams(),
    v0 = -1.0, w0 = -0.5
)
    println("=" ^ 72)
    println("DNA-0b v2: QSSA route - k_ann sweep (k_fast=$k_fast fixed)")
    println("=" ^ 72)
    @printf("%-10s %-12s %-14s %-14s %-12s\n",
        "k_ann", "v_RMSE", "P_err(QSSA)", "P_pp_mean", "drift_v")
    println("-" ^ 72)
    
    for ka in k_ann_values
        try
            sol_fhn, sol_qssa, _ = run_threeway(;
                p_fhn, k_ann=ka, k_fast, tspan, v0, w0
            )
            m = compute_threeway_metrics(sol_fhn, sol_qssa, sol_qssa)
            @printf("%-10.0f %-12.6f %-14.2e %-14s %-12.4f\n",
                ka, m.rmse_qssa, m.p_err_qssa, "-", m.drift_qssa)
        catch e
            @printf("%-10.0f FAILED: %s\n", ka, string(e)[1:min(50, end)])
        end
    end
    println("=" ^ 72)
end

# =====================================================================
# Run
# =====================================================================
if abspath(PROGRAM_FILE) == @__FILE__
    println("\n" * "=" ^ 80)
    println("EXPERIMENT 1: k_fast sweep (QSSA tracking speed)")
    println("=" ^ 80)
    results = k_fast_sweep()
    
    println("\n" * "=" ^ 80)
    println("EXPERIMENT 2: k_ann sweep for QSSA route")
    println("=" ^ 80)
    k_ann_sweep_qssa()
    
    println("\n" * "=" ^ 80)
    println("INTERPRETATION")
    println("=" ^ 80)
    println("""
    Key comparison: P_err(QSSA) vs q_err(Quad)
    
    - q_err(Quad) should GROW with time (exponential amplification via 2q self-catalysis)
    - P_err(QSSA) should STAY BOUNDED (k_fast pulls P back to v²)
    
    If P_err << q_err at t=200, the QSSA route is validated as the correct approach.
    
    The quadratization route's failure is a NEGATIVE RESULT worth reporting:
    - Hemery/Fages/Soliman (2021) pipeline is theoretically correct
    - But self-catalytic terms in quadratized systems cause exponential error growth
    - This is the first concrete demonstration for a neuroscience-relevant ODE
    
    RMSE(QSSA) vs RMSE(Quad) shows trajectory fidelity improvement.
    
    Next: if QSSA route works, proceed to:
    - DNA strand displacement reaction design
    - Full HH mapping (requires polynomialization of exp gating functions)
    """)
end
