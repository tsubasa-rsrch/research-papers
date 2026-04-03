########################################################################
# DNA-0b: FitzHugh-Nagumo → Chemical Reaction Network Simulation
# 
# Phase DNA-0a mapping (Echo, 2026):
#   FHN (2 vars) → Quadratized (3 vars, q=v²) → Dual-rail (6 vars) → CRN (24 reactions)
#
# Pipeline: Hemery, Fages, Soliman (2021) CMSB
#   Polynomialization → Quadratization → Dual-rail → Bimolecular CRN
#
# This file: DNA-0b numerical verification
#   1. Reference FHN ODE
#   2. Quadratized 3-variable ODE (verify q=v² consistency)
#   3. Dual-rail 6-variable CRN ODE
#   4. Comparison: trajectory, oscillation period/amplitude, q-v² drift
########################################################################

using OrdinaryDiffEq
using Statistics
using Printf

# =====================================================================
# FHN Parameters (standard excitable/oscillatory regime)
# =====================================================================
Base.@kwdef struct FHNParams
    a::Float64 = 0.7
    b::Float64 = 0.8
    ε::Float64 = 0.08    # timescale separation
    I::Float64 = 0.5     # external current (oscillatory regime)
end

# =====================================================================
# 1. Reference FHN ODE
#    dv/dt = v - v³/3 - w + I
#    dw/dt = ε(v + a - bw)
# =====================================================================
function fhn_ode!(du, u, p::FHNParams, t)
    v, w = u
    du[1] = v - v^3/3 - w + p.I
    du[2] = p.ε * (v + p.a - p.b * w)
end

# =====================================================================
# 2. Quadratized ODE (3 variables: v, w, q where q = v²)
#    dv/dt = v - qv/3 - w + I
#    dw/dt = ε(v + a - bw)
#    dq/dt = 2q - 2q²/3 - 2vw + 2vI
#
#    Consistency condition: q(t) = v(t)² for all t
#    (automatically satisfied if q(0) = v(0)²)
# =====================================================================
function quadratized_ode!(du, u, p::FHNParams, t)
    v, w, q = u
    du[1] = v - q*v/3 - w + p.I
    du[2] = p.ε * (v + p.a - p.b * w)
    du[3] = 2*q - 2*q^2/3 - 2*v*w + 2*v*p.I
end

# =====================================================================
# 3. Dual-rail CRN ODE (6 variables: v⁺, v⁻, w⁺, w⁻, q⁺, q⁻)
#    All variables >= 0 (concentrations)
#    v = v⁺ - v⁻,  w = w⁺ - w⁻,  q = q⁺ - q⁻
#
#    CRN reaction list (24 bimolecular/unimolecular reactions):
#
#    --- v⁺ reactions ---
#    R1:  v⁺ →[1]    2v⁺                  (autocatalytic growth)
#    R2:  q⁺+v⁻ →[1/3] q⁺+v⁻+v⁺          (cubic suppression, positive part)
#    R3:  q⁻+v⁺ →[1/3] q⁻+2v⁺             (cubic suppression, positive part)
#    R4:  w⁻ →[1]    w⁻+v⁺                (w coupling)
#    R5:  ∅ →[I]     v⁺                   (external input)
#    R6:  v⁺+v⁻ →[k_ann] ∅               (annihilation)
#
#    --- v⁻ reactions ---
#    R7:  v⁻ →[1]    2v⁻                  (autocatalytic growth)
#    R8:  q⁺+v⁺ →[1/3] q⁺+v⁺+v⁻          (cubic suppression, negative part)
#    R9:  q⁻+v⁻ →[1/3] q⁻+2v⁻             (cubic suppression, negative part)
#    R10: w⁺ →[1]    w⁺+v⁻                (w coupling)
#
#    --- w⁺ reactions ---
#    R11: v⁺ →[ε]    v⁺+w⁺                (excitation)
#    R12: ∅ →[εa]    w⁺                   (constant drive)
#    R13: w⁻ →[εb]   w⁻+w⁺                (recovery cross-term)
#    R14: w⁺+w⁻ →[k_ann] ∅               (annihilation)
#
#    --- w⁻ reactions ---
#    R15: v⁻ →[ε]    v⁻+w⁻                (excitation)
#    R16: w⁺ →[εb]   w⁺+w⁻                (recovery cross-term)
#
#    --- q⁺ reactions ---
#    R17: q⁺ →[2]    2q⁺                  (autocatalytic)
#    R18: q⁺+q⁻ →[4/3] q⁺+q⁻+q⁺          (quadratic suppression cross-term)
#    R19: v⁺+w⁻ →[2] v⁺+w⁻+q⁺            (vw coupling)
#    R20: v⁻+w⁺ →[2] v⁻+w⁺+q⁺            (vw coupling)
#    R21: v⁺ →[2I]   v⁺+q⁺                (input coupling)
#    R22: q⁺+q⁻ →[k_ann] ∅               (annihilation)
#
#    --- q⁻ reactions ---
#    R23: q⁻ →[2]    2q⁻                  (autocatalytic)
#    R24: q⁺+q⁺ →[2/3] 2q⁺+q⁻            (quadratic suppression, q⁺² term)
#    R25: q⁻+q⁻ →[2/3] q⁻+q⁻+q⁻  = 3q⁻   (quadratic suppression, q⁻² term)
#    R26: v⁺+w⁺ →[2] v⁺+w⁺+q⁻            (vw coupling)
#    R27: v⁻+w⁻ →[2] v⁻+w⁻+q⁻            (vw coupling)
#    R28: v⁻ →[2I]   v⁻+q⁻                (input coupling)
# =====================================================================

Base.@kwdef struct CRNParams
    fhn::FHNParams = FHNParams()
    k_ann::Float64 = 100.0   # annihilation rate (key parameter for DNA-0b sweep)
end

function crn_ode!(du, u, p::CRNParams, t)
    vp, vm, wp, wm, qp, qm = u   # v⁺, v⁻, w⁺, w⁻, q⁺, q⁻
    (; a, b, ε, I) = p.fhn
    k = p.k_ann
    
    # Annihilation terms (shared)
    ann_v = k * vp * vm
    ann_w = k * wp * wm
    ann_q = k * qp * qm
    
    # dv⁺/dt
    du[1] = (
        vp                       # R1:  autocatalytic
        + (qp*vm + qm*vp)/3     # R2,R3: cubic suppression (positive part of -qv/3)
        + wm                     # R4:  -w positive part
        + I                      # R5:  external input
        - ann_v                  # R6:  annihilation
    )
    
    # dv⁻/dt
    du[2] = (
        vm                       # R7:  autocatalytic
        + (qp*vp + qm*vm)/3     # R8,R9: cubic suppression (negative part of -qv/3)
        + wp                     # R10: -w negative part
        - ann_v                  # R6:  annihilation (shared)
    )
    
    # dw⁺/dt
    du[3] = (
        ε * vp                   # R11: excitation
        + ε * a                  # R12: constant drive
        + ε * b * wm             # R13: recovery cross-term
        - ann_w                  # R14: annihilation
    )
    
    # dw⁻/dt
    du[4] = (
        ε * vm                   # R15: excitation
        + ε * b * wp             # R16: recovery cross-term
        - ann_w                  # R14: annihilation (shared)
    )
    
    # dq⁺/dt
    du[5] = (
        2*qp                     # R17: autocatalytic
        + (4/3)*qp*qm           # R18: quadratic suppression cross-term
        + 2*(vp*wm + vm*wp)     # R19,R20: vw coupling
        + 2*I*vp                 # R21: input coupling
        - ann_q                  # R22: annihilation
    )
    
    # dq⁻/dt
    du[6] = (
        2*qm                     # R23: autocatalytic
        + (2/3)*(qp^2 + qm^2)  # R24,R25: quadratic suppression (q⁺² + q⁻²)
        + 2*(vp*wp + vm*wm)     # R26,R27: vw coupling
        + 2*I*vm                 # R28: input coupling
        - ann_q                  # R22: annihilation (shared)
    )
end

# =====================================================================
# Initial condition conversion
# =====================================================================
function fhn_to_dualrail(v0, w0)
    # Dual-rail encoding: x = x⁺ - x⁻, with x⁺,x⁻ >= 0
    vp = max(v0, 0.0)
    vm = max(-v0, 0.0)
    wp = max(w0, 0.0)
    wm = max(-w0, 0.0)
    
    # q = v², always non-negative, so q⁺ = v², q⁻ = 0
    q0 = v0^2
    qp = q0
    qm = 0.0
    
    return [vp, vm, wp, wm, qp, qm]
end

function dualrail_to_fhn(u_crn)
    vp, vm, wp, wm, qp, qm = u_crn
    v = vp - vm
    w = wp - wm
    q = qp - qm
    return v, w, q
end

# =====================================================================
# Simulation and comparison
# =====================================================================
function run_comparison(;
    p_fhn = FHNParams(),
    k_ann = 100.0,
    tspan = (0.0, 200.0),
    v0 = -1.0,
    w0 = -0.5,
    solver = Rodas5P(),          # stiff solver (annihilation makes it stiff)
    abstol = 1e-10,
    reltol = 1e-8,
    saveat = 0.01
)
    # --- FHN reference ---
    prob_fhn = ODEProblem(fhn_ode!, [v0, w0], tspan, p_fhn)
    sol_fhn = solve(prob_fhn, solver; abstol, reltol, saveat)
    
    # --- Quadratized ---
    q0 = v0^2
    prob_quad = ODEProblem(quadratized_ode!, [v0, w0, q0], tspan, p_fhn)
    sol_quad = solve(prob_quad, solver; abstol, reltol, saveat)
    
    # --- CRN dual-rail ---
    u0_crn = fhn_to_dualrail(v0, w0)
    p_crn = CRNParams(fhn=p_fhn, k_ann=k_ann)
    prob_crn = ODEProblem(crn_ode!, u0_crn, tspan, p_crn)
    sol_crn = solve(prob_crn, solver; abstol, reltol, saveat)
    
    return sol_fhn, sol_quad, sol_crn
end

function compute_metrics(sol_fhn, sol_quad, sol_crn; skip_transient=50.0, dt=0.01)
    # Extract time points after transient
    ts = sol_fhn.t[sol_fhn.t .>= skip_transient]
    idx_fhn = findall(t -> t >= skip_transient, sol_fhn.t)
    idx_quad = findall(t -> t >= skip_transient, sol_quad.t)
    idx_crn = findall(t -> t >= skip_transient, sol_crn.t)
    
    # FHN reference
    v_fhn = [sol_fhn[1, i] for i in idx_fhn]
    w_fhn = [sol_fhn[2, i] for i in idx_fhn]
    
    # Quadratized: check q = v² consistency
    v_quad = [sol_quad[1, i] for i in idx_quad]
    w_quad = [sol_quad[2, i] for i in idx_quad]
    q_quad = [sol_quad[3, i] for i in idx_quad]
    q_error_quad = sqrt(mean((q_quad .- v_quad.^2).^2))
    
    # CRN dual-rail
    v_crn = [sol_crn[1,i] - sol_crn[2,i] for i in idx_crn]   # v⁺ - v⁻
    w_crn = [sol_crn[3,i] - sol_crn[4,i] for i in idx_crn]   # w⁺ - w⁻
    q_crn = [sol_crn[5,i] - sol_crn[6,i] for i in idx_crn]   # q⁺ - q⁻
    v_crn_sq = v_crn.^2
    q_error_crn = sqrt(mean((q_crn .- v_crn_sq).^2))
    
    # Trajectory RMSE (CRN vs FHN)
    # Use interpolation for fair comparison
    n = min(length(v_fhn), length(v_crn))
    v_rmse = sqrt(mean((v_fhn[1:n] .- v_crn[1:n]).^2))
    w_rmse = sqrt(mean((w_fhn[1:n] .- w_crn[1:n]).^2))
    
    # Dual-rail drift: how much do v⁺ and v⁻ grow beyond what's needed?
    vp_crn = [sol_crn[1,i] for i in idx_crn]
    vm_crn = [sol_crn[2,i] for i in idx_crn]
    drift_v = mean(min.(vp_crn, vm_crn))  # ideally 0 if annihilation is perfect
    
    return (
        v_rmse = v_rmse,
        w_rmse = w_rmse,
        q_error_quad = q_error_quad,
        q_error_crn = q_error_crn,
        drift_v = drift_v,
    )
end

# =====================================================================
# k_ann sweep (core DNA-0b experiment)
# Analogous to CA3 tau sweep
# =====================================================================
function k_ann_sweep(;
    k_ann_values = [1.0, 5.0, 10.0, 50.0, 100.0, 500.0, 1000.0],
    tspan = (0.0, 200.0),
    p_fhn = FHNParams(),
    v0 = -1.0, w0 = -0.5
)
    println("=" ^ 72)
    println("DNA-0b: k_ann sweep (annihilation rate vs FHN fidelity)")
    println("FHN params: a=$(p_fhn.a), b=$(p_fhn.b), ε=$(p_fhn.ε), I=$(p_fhn.I)")
    println("=" ^ 72)
    @printf("%-10s %-12s %-12s %-14s %-14s %-12s\n",
        "k_ann", "v_RMSE", "w_RMSE", "q_err(quad)", "q_err(CRN)", "drift_v")
    println("-" ^ 72)
    
    results = []
    for k in k_ann_values
        try
            sol_fhn, sol_quad, sol_crn = run_comparison(;
                p_fhn, k_ann=k, tspan, v0, w0
            )
            m = compute_metrics(sol_fhn, sol_quad, sol_crn)
            @printf("%-10.1f %-12.6f %-12.6f %-14.2e %-14.2e %-12.4f\n",
                k, m.v_rmse, m.w_rmse, m.q_error_quad, m.q_error_crn, m.drift_v)
            push!(results, (k_ann=k, m...))
        catch e
            @printf("%-10.1f FAILED: %s\n", k, string(e)[1:min(50, end)])
            push!(results, (k_ann=k, v_rmse=NaN, w_rmse=NaN,
                           q_error_quad=NaN, q_error_crn=NaN, drift_v=NaN))
        end
    end
    
    println("=" ^ 72)
    return results
end

# =====================================================================
# Run
# =====================================================================
if abspath(PROGRAM_FILE) == @__FILE__
    results = k_ann_sweep()
    
    println("\nInterpretation:")
    println("- v_RMSE, w_RMSE: trajectory deviation of CRN from FHN (lower = better)")
    println("- q_err(quad): q - v² in quadratized system (should be ~machine epsilon)")
    println("- q_err(CRN): q - v² in CRN system (depends on k_ann)")
    println("- drift_v: min(v⁺,v⁻) mean (annihilation effectiveness, 0 = perfect)")
    println()
    println("Key question: at what k_ann does CRN faithfully reproduce FHN oscillation?")
    println("Compare with CA3 tau sweep structure.")
end
