import matplotlib.pyplot as plt
import numpy as np


class CreateGraphics:

    @staticmethod
    def plotAuthoringFiles(targetDev):

        # -------------------------
        # Dados
        # -------------------------
        authoring_files = targetDev.authoringFiles

        if not authoring_files:
            print("Nenhum arquivo de autoria encontrado.")
            return

        labels = list(authoring_files.keys())
        values = list(authoring_files.values())

        # -------------------------
        # Paleta
        # -------------------------
        base_colors = [
            "#0284c7",
            "#38bdf8",
            "#06b6d4",
            "#a855f7",
            "#22c55e",
            "#f97316",
        ]

        colors = [base_colors[i % len(base_colors)] for i in range(len(labels))]

        grid_color = "#e5e7eb"
        text_primary = "#111827"
        text_secondary = "#4b5563"

        # -------------------------
        # Figura
        # -------------------------
        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=160)

        fig.patch.set_alpha(0)
        ax.set_facecolor('none')

        x = np.arange(len(labels))

        # -------------------------
        # Sombra
        # -------------------------
        ax.bar(
            x + 0.04,
            values,
            width=0.55,
            color="#000000",
            alpha=0.06,
            linewidth=0
        )

        # -------------------------
        # Barras
        # -------------------------
        bars = ax.bar(
            x,
            values,
            width=0.55,
            color=colors,
            edgecolor="none"
        )

        # -------------------------
        # Eixos e grid
        # -------------------------
        ax.set_ylim(0, max(values) * 1.15)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, color=text_secondary)

        ax.tick_params(axis='y', labelsize=8, colors=text_secondary)

        ax.yaxis.grid(True, color=grid_color, linewidth=1)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        # -------------------------
        # Valores nas barras
        # -------------------------
        for bar in bars:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + max(values) * 0.02,
                f"{int(h)}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=text_primary
            )

        # -------------------------
        # Layout + salvar
        # -------------------------
        plt.tight_layout(pad=0.6)

        plt.savefig(
            "testeGrafico/graficoAuthoringFilesPorLinguagem.png",
            dpi=160,
            bbox_inches="tight",
            transparent=True
        )

        plt.close()


    @staticmethod
    def plotCommitsByLanguage(targetDev, GITHUB_TOKEN):

        # -------------------------
        # Buscar dados
        # -------------------------
        targetDev.getCommitsByLanguage(GITHUB_TOKEN)

        labels = [item["linguagem"] for item in targetDev.totalCommits]
        values = [item["totalCommits"] for item in targetDev.totalCommits]

        if not labels:
            print("Nenhum commit encontrado para este desenvolvedor.")
            return

        # -------------------------
        # Paleta
        # -------------------------
        base_colors = [
            "#0284c7",
            "#38bdf8",
            "#06b6d4",
            "#a855f7",
            "#22c55e",
            "#f97316",
        ]

        colors = [base_colors[i % len(base_colors)] for i in range(len(labels))]

        grid_color = "#e5e7eb"
        text_primary = "#111827"
        text_secondary = "#4b5563"

        # -------------------------
        # Figura
        # -------------------------
        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=160)

        fig.patch.set_alpha(0)
        ax.set_facecolor('none')

        x = np.arange(len(labels))

        # -------------------------
        # Sombra
        # -------------------------
        ax.bar(
            x + 0.04,
            values,
            width=0.55,
            color="#000000",
            alpha=0.06,
            linewidth=0
        )

        # -------------------------
        # Barras
        # -------------------------
        bars = ax.bar(
            x,
            values,
            width=0.55,
            color=colors,
            edgecolor="none"
        )

        # -------------------------
        # Eixos e grid
        # -------------------------
        ax.set_ylim(0, max(values) * 1.15)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, color=text_secondary)

        ax.tick_params(axis='y', labelsize=8, colors=text_secondary)

        ax.yaxis.grid(True, color=grid_color, linewidth=1)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)


        # -------------------------
        # Valores nas barras
        # -------------------------
        for bar in bars:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + max(values) * 0.02,
                f"{int(h)}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=text_primary
            )

        # -------------------------
        # Layout + salvar
        # -------------------------
        plt.tight_layout(pad=0.6)

        plt.savefig(
            "testeGrafico/graficoCommitsPorLinguagem.png",
            dpi=160,
            bbox_inches="tight",
            transparent=True
        )

        plt.close()


    @staticmethod
    def plotLinesByLanguage(targetDev):

        # -------------------------
        # Dados vindos do método
        # -------------------------
        totais_por_linguagem = {}

        for repo in targetDev.linesAddRemov:
            linguagem = repo["linguagem"]
            total_linhas = repo["linhaAdd"] + repo["linhaRemov"]

            totais_por_linguagem[linguagem] = (
                totais_por_linguagem.get(linguagem, 0) + total_linhas
            )

        labels = list(totais_por_linguagem.keys())
        values = list(totais_por_linguagem.values())

        # -------------------------
        # Paleta (ajustada dinamicamente)
        # -------------------------
        base_colors = [
            "#0284c7",
            "#38bdf8",
            "#06b6d4",
            "#a855f7",
            "#22c55e",
            "#f97316",
        ]

        colors = [base_colors[i % len(base_colors)] for i in range(len(labels))]

        bg_color = "#f9fafb"
        grid_color = "#e5e7eb"
        text_primary = "#111827"
        text_secondary = "#4b5563"

        # -------------------------
        # Figura
        # -------------------------
        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=160)

        fig.patch.set_alpha(0)
        ax.set_facecolor('none')

        x = np.arange(len(labels))

        # -------------------------
        # Sombra
        # -------------------------
        ax.bar(
            x + 0.04,
            values,
            width=0.55,
            color="#000000",
            alpha=0.06,
            linewidth=0
        )

        # -------------------------
        # Barras
        # -------------------------
        bars = ax.bar(
            x,
            values,
            width=0.55,
            color=colors,
            edgecolor="none"
        )

        # -------------------------
        # Eixos e grid
        # -------------------------
        ax.set_ylim(0, max(values) * 1.15)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, color=text_secondary)

        ax.tick_params(axis='y', labelsize=8, colors=text_secondary)

        ax.yaxis.grid(True, color=grid_color, linewidth=1)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)


        # -------------------------
        # Valores nas barras
        # -------------------------
        for bar in bars:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + max(values) * 0.02,
                f"{int(h)}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=text_primary
            )

        # -------------------------
        # Layout + salvar
        # -------------------------
        plt.tight_layout(pad=0.6)

        plt.savefig(
            "testeGrafico/graficoLinhasPorLinguagem.png",
            dpi=160,
            bbox_inches="tight",
            transparent=True
        )

        plt.close()
