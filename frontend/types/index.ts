
export interface BaziProfile {
    day_master: string
    day_master_element: string
    strength: "身強" | "身弱" | "中和"
    structure: string
    favorable: string[]
    unfavorable: string[]
}

export interface Persona {
    id: string
    name: string
    age: string
    element: string
    day_master: string
    pattern: string // structure alias
    trait: string
    location?: string
    decision_logic?: string
    occupation?: string

    // Bazi Extended
    birth_year?: number
    birth_month?: number
    birth_day?: number
    birth_shichen?: string
    four_pillars?: string
    strength?: string
    favorable?: string[]

    // UI Logic (Hydrated)
    current_luck?: { name: string; description: string }
    luck_timeline?: { age_start: number; age_end: number; name: string; description: string }[]

    displayAge?: string
    fullBirthday?: string
    luckCycle?: string
    detailedTrait?: string
}

export interface SimulationData {
    status: string
    score: number
    summary: string
    genesis: {
        sample_size: number
        personas: Persona[]
    }
    arena_comments: Array<{
        sentiment: string
        text: string
        citizen_id?: string
        persona: Persona
    }>
    // Analysis
    intent?: string
    suggestions?: Array<{ target: string; advice: string; execution_plan: string[]; score_improvement?: string }>
    objections?: Array<{ reason: string; percentage: string }>
}

export interface CitizenFilter {
    page?: number
    limit?: number
    search?: string
    element?: string
    structure?: string
}
