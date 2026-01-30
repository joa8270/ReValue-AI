
import { Persona, SimulationData, CitizenFilter, Skill, BaZiRequest } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
    // Skills
    async getSkills(): Promise<Skill[]> {
        try {
            const res = await fetch(`${API_URL}/api/skills`);
            if (res.ok) {
                return await res.json();
            }
            console.warn("Failed to fetch skills");
            return [];
        } catch (error) {
            console.error("API/Skills: Error", error);
            // Return Mock Skills for Plan Mode visualization if backend is offline
            return [
                { id: "1", slug: "bazi-calc", name: "BaZi Calculator", description: "Calculate Four Pillars based on birth date.", version: "1.0" },
                { id: "2", slug: "demo-skill", name: "Demo Skill", description: "A placeholder for future skills.", version: "0.1" }
            ];
        }
    },

    async executeBaZiCalc(data: BaZiRequest): Promise<any> {
        try {
            const res = await fetch(`${API_URL}/api/skills/bazi-calc/execute`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                return await res.json();
            }
            throw new Error("Execution failed");
        } catch (error) {
            console.error("API/BaZi: Error", error);
            throw error;
        }
    },

    // Citizens

    async getCitizens(filter?: CitizenFilter): Promise<Persona[]> {
        try {
            // Fallback strategy: Fetch a "Master" simulation to represent the population.
            const res = await fetch(`${API_URL}/citizens`);
            if (res.ok) {
                const data = await res.json();
                return data.map((p: any) => this.enrichPersona(p));
            }
            throw new Error("Endpoint not found");
        } catch (error) {
            console.warn("API/Citizens: Using Fallback Mock Data");
            return [];
        }
    },

    // Simulation
    async getSimulation(id: string): Promise<SimulationData | null> {
        try {
            const res = await fetch(`${API_URL}/simulation/${id}`);
            if (!res.ok) throw new Error("Failed");
            return await res.json();
        } catch (error) {
            console.error("Failed to fetch simulation", error);
            return null;
        }
    },

    // Utils: Enrich Data
    enrichPersona(p: Persona): Persona {
        let dm = p.day_master;

        // Element Mapping
        if ((!dm || dm === "未知") && !p.four_pillars) {
            const dmMap: Record<string, string[]> = {
                "Fire": ["丙火", "丁火"], "Water": ["壬水", "癸水"], "Metal": ["庚金", "辛金"], "Wood": ["甲木", "乙木"], "Earth": ["戊土", "己土"]
            }
            const options = dmMap[p.element] || ["甲木"];
            dm = options[Math.floor(Math.random() * options.length)];
        }

        // Timeline Mock
        let luck_timeline = p.luck_timeline || [];
        if (luck_timeline.length === 0) {
            const startAge = Math.floor(Math.random() * 8) + 2;
            const pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉"];
            for (let i = 0; i < 8; i++) {
                luck_timeline.push({
                    age_start: startAge + (i * 10),
                    age_end: startAge + (i * 10) + 9,
                    name: pillars[i % 10] + "運",
                    description: "運勢平穩，適合發展。"
                });
            }
        }

        return {
            ...p,
            day_master: dm,
            luck_timeline,
            strength: p.strength || "身強",
            favorable: p.favorable || ["木", "火"],
            decision_logic: p.decision_logic?.includes("根據") ? "【邏輯審慎型】決策前必先評估風險。" : (p.decision_logic || "【多元策略型】能根據不同情境調整。")
        };
    }
}
