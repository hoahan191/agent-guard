# AgentGuard: DevSecOps Trust Layer

```mermaid
flowchart TB
    subgraph CI["GitHub Actions (DevSecOps Pipeline)"]
        PR[Lập trình viên mở Pull Request]
        GHA[GitHub Action Runner]
        PR_Comment[Bot Comment cảnh báo trên PR]
    end

    subgraph GCP["Google Cloud Platform (Zero-Trust Security)"]
        WIF{Workload Identity<br/>Federation - OIDC}
        Vertex[Vertex AI<br/>Gemini API]
    end

    subgraph AgentGuard["AgentGuard CLI Tool"]
        Orchestrator((Antigravity<br/>Manager))

        subgraph Agents["The Adversarial Triad"]
            Attacker[Attacker Agent<br/>Red Team: Gemini 1.5 Flash]
            Judge[Judge Agent<br/>Referee: Gemini 1.5 Pro]
        end

        MCP[(Jailbreak Arsenal<br/>MCP Server)]
    end

    subgraph Target["Môi trường Staging"]
        TargetAPI[Target Agent API<br/>Blue Team]
    end

    %% Flow Logic
    PR -->|1. Kích hoạt Workflow| GHA
    GHA -->|2. Trao đổi OIDC Token| WIF
    WIF -->|3. Trả về Token ngắn hạn| GHA

    GHA -->|4. Lệnh: agent-guard scan| Orchestrator
    Orchestrator -->|5. Khởi tạo State & Cấp quyền| Attacker
    
    Attacker <-->|6. Lấy Attack Vector| MCP
    Attacker <-->|Inference| Vertex
    Attacker -->|7. Gửi Payload Độc hại| TargetAPI
    TargetAPI -->|8. Trả về kết quả| Orchestrator

    Orchestrator -->|9. Chuyển giao Context Window| Judge
    Judge <-->|Inference & Suy luận sâu| Vertex
    
    Judge -->|10. Trả về Báo cáo JSON| Orchestrator
    Orchestrator -->|11. Quyết định Exit Code (0/1)| GHA
    GHA -->|12. Hiển thị 🔴 BLOCKED / 🟢 PASSED| PR_Comment

    %% Styling cho sự trực quan
    classDef secure fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef danger fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000;
    classDef gcp fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#000;
    classDef neutral fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000;

    class WIF,Vertex gcp;
    class Attacker,MCP danger;
    class TargetAPI secure;
    class Orchestrator,Judge core;
    class PR,GHA,PR_Comment neutral;
```
