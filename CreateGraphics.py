import matplotlib.pyplot as plt
import numpy as np


class CreateGraphics:

    # -------------------------
    # Configurações visuais
    # -------------------------
    BASE_COLORS = [
        "#0284c7",
        "#38bdf8",
        "#06b6d4",
        "#a855f7",
        "#22c55e",
        "#f97316",
    ]

    GRID_COLOR = "#e5e7eb"
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#4b5563"

    FIG_SIZE = (5, 3.2)
    DPI = 160
    BAR_WIDTH = 0.55

    #Grafico generico
    @staticmethod
    def _plot_bar_chart(labels, values, output_path):

        if not labels or not values:
            print("Sem dados para gerar gráfico.")
            return

        colors = [
            CreateGraphics.BASE_COLORS[i % len(CreateGraphics.BASE_COLORS)]
            for i in range(len(labels))
        ]

        fig, ax = plt.subplots(figsize=CreateGraphics.FIG_SIZE, dpi=CreateGraphics.DPI)

        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        x = np.arange(len(labels))

        # sombra
        ax.bar(
            x + 0.04,
            values,
            width=CreateGraphics.BAR_WIDTH,
            color="#000000",
            alpha=0.06,
            linewidth=0,
        )

        # barras principais
        bars = ax.bar(
            x,
            values,
            width=CreateGraphics.BAR_WIDTH,
            color=colors,
            edgecolor="none",
        )

        # eixos
        ax.set_ylim(0, max(values) * 1.15)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9, color=CreateGraphics.TEXT_SECONDARY)

        ax.tick_params(axis="y", labelsize=8, colors=CreateGraphics.TEXT_SECONDARY)

        ax.yaxis.grid(True, color=CreateGraphics.GRID_COLOR, linewidth=1)
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        # valores nas barras
        for bar in bars:
            h = bar.get_height()

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + max(values) * 0.02,
                f"{int(h)}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=CreateGraphics.TEXT_PRIMARY,
            )

        plt.tight_layout(pad=0.6)

        plt.savefig(
            output_path,
            dpi=CreateGraphics.DPI,
            bbox_inches="tight",
            transparent=True,
        )

        plt.close()

 
    @staticmethod
    def plotAuthoringFiles(targetDev):

        authoring_files = targetDev.authoringFiles

        if not authoring_files:
            print("Nenhum arquivo de autoria encontrado.")
            return

        labels = list(authoring_files.keys())
        values = list(authoring_files.values())

        CreateGraphics._plot_bar_chart(
            labels,
            values,
            "graficos/graficoAuthoringFilesPorLinguagem.png",
        )


    @staticmethod
    def plotCommitsByLanguage(targetDev):

        labels = [item["linguagem"] for item in targetDev.totalCommits]
        values = [item["totalCommits"] for item in targetDev.totalCommits]

        if not labels:
            print("Nenhum commit encontrado para este desenvolvedor.")
            return

        CreateGraphics._plot_bar_chart(
            labels,
            values,
            "graficos/graficoCommitsPorLinguagem.png",
        )


    @staticmethod
    def plotLinesByLanguage(targetDev):

        totais_por_linguagem = {}

        for repo in targetDev.linesAddRemov:
            linguagem = repo["linguagem"]
            total_linhas = repo["linhaAdd"] + repo["linhaRemov"]

            totais_por_linguagem[linguagem] = (
                totais_por_linguagem.get(linguagem, 0) + total_linhas
            )

        labels = list(totais_por_linguagem.keys())
        values = list(totais_por_linguagem.values())

        CreateGraphics._plot_bar_chart(
            labels,
            values,
            "graficos/graficoLinhasPorLinguagem.png",
        )