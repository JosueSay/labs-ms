import os
import pygame

from core.controller import SimulationController
from io_mm1.config_loader import loadConfig


def initPygame(width=900, height=450):
    # inicializa pygame y la ventana
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Simulación M/M/1")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    return screen, clock, font


def createController():
    # carga config por defecto y crea un controller
    cfg_path = os.path.join("configs", "default.yaml")
    cfg = loadConfig(cfg_path)

    model_cfg = cfg["model"]
    model_params = cfg["model_params"]
    sim_cfg = cfg["simulation"]
    seed = cfg["project"]["seed"]

    controller = SimulationController(model_cfg, model_params, sim_cfg, rng_seed=seed)
    # usamos tickWithDelta, no dependemos de controller.speed
    return controller, cfg


def drawText(surface, font, text, x, y, color):
    # dibuja texto simple
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def drawQueue(surface, font, model, sim_width, sim_height):
    # dibuja la cola de clientes como círculos
    queue = list(model.queue)
    queue_len = len(queue)

    base_x = 80
    base_y = sim_height // 2 + 20
    radius = 10
    spacing = 28
    max_draw = 15

    color_circle = (80, 160, 240)
    color_outline = (30, 80, 140)

    for idx, _ in enumerate(queue[:max_draw]):
        cx = base_x + idx * spacing
        cy = base_y
        pygame.draw.circle(surface, color_circle, (cx, cy), radius)
        pygame.draw.circle(surface, color_outline, (cx, cy), radius, 1)

    if queue_len > max_draw:
        extra = queue_len - max_draw
        drawText(surface, font, f"+{extra} más", base_x + max_draw * spacing, base_y - 18, (200, 200, 200))

    drawText(surface, font, f"cola (Lq): {queue_len}", base_x, base_y + 28, (230, 230, 230))


def drawServer(surface, font, model, sim_width, sim_height):
    # dibuja servidor como un rectángulo
    server_state = model.server_state
    rect_width = 140
    rect_height = 90

    x = sim_width - rect_width - 80
    y = sim_height // 2 - rect_height // 2 + 10

    if server_state == "busy":
        color_fill = (240, 120, 120)
    else:
        color_fill = (120, 220, 140)

    color_border = (30, 30, 30)

    pygame.draw.rect(surface, color_fill, (x, y, rect_width, rect_height))
    pygame.draw.rect(surface, color_border, (x, y, rect_width, rect_height), 2)

    text_state = f"servidor: {server_state}"
    drawText(surface, font, text_state, x + 8, y + rect_height + 8, (230, 230, 230))


def drawHud(surface, font, controller, cfg, sim_width, sim_hours_per_second, ended):
    # dibuja info básica de la simulación
    snapshot = controller.getSnapshot(include_series=False)
    model_state = snapshot.get("model_state", {}) or {}

    sim_time = model_state.get("sim_time", 0.0)
    n_created = model_state.get("n_customers_created", 0)
    n_completed = model_state.get("n_customers_completed", 0)
    rho_avg = model_state.get("rho_avg_so_far", None)
    end_time = snapshot.get("end_time", None)

    drawText(surface, font, f"Tiempo de simulación (horas): {sim_time:.3f}", 20, 18, (230, 230, 230))
    drawText(surface, font, f"Clientes creados: {n_created}", 20, 40, (230, 230, 230))
    drawText(surface, font, f"Clientes completados: {n_completed}", 20, 62, (230, 230, 230))

    if rho_avg is not None:
        drawText(surface, font, f"Utilización promedio (rho): {rho_avg:.3f}", 20, 84, (230, 230, 230))
    else:
        drawText(surface, font, "Utilización promedio (rho): n/a", 20, 84, (230, 230, 230))


    if end_time is not None and end_time > 0:
        progress = min(100.0, max(0.0, 100.0 * sim_time / end_time))
        drawText(
            surface,
            font,
            f"Objetivo (h): {end_time:.2f} - Progreso: {progress:.1f}%",
            20,
            108,
            (210, 210, 210),
        )

    drawText(
        surface,
        font,
        f"Velocidad: {sim_hours_per_second:.3f} h/s",
        sim_width - 320,
        18,
        (200, 200, 200),
    )

    drawText(
        surface,
        font,
        "Controles: ESC=cerrar - SPACE=pausa/reanudar - ↑/↓ o +/- = velocidad - R=reset",
        20,
        132,
        (180, 180, 180),
    )

    if ended:
        drawText(
            surface,
            font,
            "Simulación terminada (se alcanzó el tiempo objetivo)",
            20,
            156,
            (250, 140, 140),
        )


def mainLoop():
    screen, clock, font = initPygame()
    sim_width, sim_height = screen.get_size()

    controller, cfg = createController()
    paused = False

    # horas de simulación avanzadas por segundo real (controlable con teclas)
    sim_hours_per_second = 0.25  # 0.25h = 15 minutos de simul por segundo

    running = True
    while running:
        dt_ms = clock.tick(60)
        dt_sec = dt_ms / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key in (pygame.K_UP, pygame.K_KP_PLUS):
                    sim_hours_per_second *= 2.0
                    if sim_hours_per_second > 8.0:
                        sim_hours_per_second = 8.0
                if event.key in (pygame.K_DOWN, pygame.K_KP_MINUS):
                    sim_hours_per_second *= 0.5
                    if sim_hours_per_second < 0.01:
                        sim_hours_per_second = 0.01
                if event.key == pygame.K_r:
                    controller.resetSimulation()
                    paused = False

        snapshot_before = controller.getSnapshot(include_series=False)
        ended_before = snapshot_before.get("ended", False)

        if not paused and not ended_before:
            sim_delta_hours = sim_hours_per_second * dt_sec
            if sim_delta_hours > 0:
                controller.tickWithDelta(sim_delta_hours, collect_series=False)

        snapshot = controller.getSnapshot(include_series=False)
        ended = snapshot.get("ended", False)
        if ended:
            paused = True

        screen.fill((25, 25, 30))

        if controller.model is not None:
            drawHud(screen, font, controller, cfg, sim_width, sim_hours_per_second, ended)
            drawQueue(screen, font, controller.model, sim_width, sim_height)
            drawServer(screen, font, controller.model, sim_width, sim_height)

        if paused and not ended:
            drawText(screen, font, "[PAUSADO]", sim_width // 2 - 60, sim_height - 40, (240, 220, 120))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    mainLoop()
