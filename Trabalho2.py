import matplotlib.pyplot as plt
import random
from collections import deque

def fifo(pages_with_access, frames_count, verbose=False):
    frames = deque()
    dirty_pages = set()
    page_faults = 0
    disk_writes = 0
    log = []

    for page, access_type in pages_with_access:
        log.append(f"Acesso: ({page}, '{access_type}')")

        if page in frames:
            log.append("  -> Page Hit!")
            if access_type == 'W':
                dirty_pages.add(page)
                log.append("  -> Página marcada como 'suja' (dirty).")
        else:
            page_faults += 1
            log.append("  -> PAGE FAULT!")

            if len(frames) < frames_count:
                frames.append(page)
                log.append(f"  -> Carregando página {page} em um quadro livre.")
            else:
                victim = frames.popleft()
                log.append(f"  -> Substituindo página {victim} (FIFO).")
                if victim in dirty_pages:
                    disk_writes += 1
                    dirty_pages.remove(victim)
                    log.append("  -> Página vítima estava 'suja'. Escrita no disco.")
                frames.append(page)

            if access_type == 'W':
                dirty_pages.add(page)
                log.append("  -> Página carregada marcada como 'suja'.")

        log.append(f"  -> Estado da memória: {list(frames)}")
        log.append(f"  -> Páginas sujas: {dirty_pages}")
        log.append("-" * 30)

    if verbose:
        print("\n".join(log))

    return page_faults, disk_writes

def lru(pages_with_access, frames_count, verbose=False):
    frames = []
    dirty_pages = set()
    recent_use = {}
    page_faults = 0
    disk_writes = 0
    log = []

    for i, (page, access_type) in enumerate(pages_with_access):
        log.append(f"Acesso: ({page}, '{access_type}') no tempo {i}")

        if page in frames:
            log.append("  -> Page Hit!")
            if access_type == 'W':
                dirty_pages.add(page)
                log.append("  -> Página marcada como 'suja'.")
        else:
            page_faults += 1
            log.append("  -> PAGE FAULT!")

            if len(frames) < frames_count:
                frames.append(page)
                log.append(f"  -> Carregando página {page} em um quadro livre.")
            else:
                lru_page = min(frames, key=lambda p: recent_use.get(p, -1))
                frames.remove(lru_page)
                log.append(f"  -> Substituindo página {lru_page} (LRU).")
                if lru_page in dirty_pages:
                    disk_writes += 1
                    dirty_pages.remove(lru_page)
                    log.append("  -> Página vítima estava 'suja'. Escrita no disco.")
                frames.append(page)

            if access_type == 'W':
                dirty_pages.add(page)
                log.append("  -> Página carregada marcada como 'suja'.")

        recent_use[page] = i
        log.append(f"  -> Estado da memória: {frames}")
        log.append(f"  -> Páginas sujas: {dirty_pages}")
        log.append("-" * 30)

    if verbose:
        print("\n".join(log))

    return page_faults, disk_writes


def generate_locality_sequence_with_rw(length=100, page_range_max=50,
                                       working_set_size=5, working_set_time=15,
                                       write_probability=0.3):
    pages = []
    while len(pages) < length:
        working_set = set()
        while len(working_set) < working_set_size:
            working_set.add(random.randint(0, page_range_max - 1))

        time_in_set = 0
        while time_in_set < working_set_time and len(pages) < length:
            if random.random() < 0.8:
                page = random.choice(list(working_set))
            else:
                page = random.randint(0, page_range_max - 1)
            access_type = 'W' if random.random() < write_probability else 'R'
            pages.append((page, access_type))
            time_in_set += 1

    return pages

if __name__ == "__main__":
    MAX_FRAMES = 15
    TAMANHO_SEQUENCIA = 500
    UNIVERSO_PAGINAS = 50

    pages = generate_locality_sequence_with_rw(
        length=TAMANHO_SEQUENCIA,
        page_range_max=UNIVERSO_PAGINAS,
        working_set_size=5,
        working_set_time=20,
        write_probability=0.3
    )

    fifo_faults_results = []
    fifo_writes_results = []
    lru_faults_results = []
    lru_writes_results = []
    frame_range = range(1, MAX_FRAMES + 1)

    print("Executando análise de métricas...")
    for frames in frame_range:
        faults_f, writes_f = fifo(pages, frames)
        fifo_faults_results.append(faults_f)
        fifo_writes_results.append(writes_f)

        faults_l, writes_l = lru(pages, frames)
        lru_faults_results.append(faults_l)
        lru_writes_results.append(writes_l)

    print("--- Resultados (Page Faults e Disk Writes) ---")
    print("Quadros | FIFO (Faults/Writes) | LRU (Faults/Writes)")
    print("-" * 50)
    for i in frame_range:
        idx = i - 1
        print(f"{i:<7} | {fifo_faults_results[idx]:<7} / {fifo_writes_results[idx]:<6} | {lru_faults_results[idx]:<6} / {lru_writes_results[idx]:<6}")

    plt.figure(figsize=(12, 10))

    plt.subplot(2, 1, 1)
    plt.plot(frame_range, fifo_faults_results, marker='o', label='FIFO', linewidth=2)
    plt.plot(frame_range, lru_faults_results, marker='s', label='LRU', linewidth=2)
    plt.title("Comparação de Faltas de Página (Page Faults)")
    plt.xlabel("Número de Quadros (Frames)")
    plt.ylabel("Faltas de Página")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(frame_range, fifo_writes_results, marker='o', color='red', label='FIFO', linewidth=2)
    plt.plot(frame_range, lru_writes_results, marker='s', color='green', label='LRU', linewidth=2)
    plt.title("Comparação de Escritas no Disco (Disk Writes)")
    plt.xlabel("Número de Quadros (Frames)")
    plt.ylabel("Escritas no Disco")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.show()

    print("\n" + "="*60)
    print("ILUSTRAÇÃO DO FUNCIONAMENTO (simulação detalhada)")
    print("="*60 + "\n")

    pages_curtas = pages[:20]
    print("--- INÍCIO LOG LRU (verbose=True) ---")
    faults, writes = lru(pages_curtas, 3, verbose=True)
    print("--- FIM LOG LRU ---")
    print(f"\nResultado (LRU com 3 quadros): {faults} Page Faults, {writes} Disk Writes\n")

    print("--- INÍCIO LOG FIFO (verbose=True) ---")
    faults, writes = fifo(pages_curtas, 3, verbose=True)
    print("--- FIM LOG FIFO ---")
    print(f"\nResultado (FIFO com 3 quadros): {faults} Page Faults, {writes} Disk Writes\n")

    print("\n==============================")
    print("EXEMPLOS DE ENTRADA / SAÍDA (Aleatórios)")
    print("==============================")

    exemplos = [(generate_locality_sequence_with_rw(length=10, page_range_max=6, write_probability=0.4), frames)
                for frames in [3, 4, 5]]

    for i, (seq, frames) in enumerate(exemplos, start=1):
        print(f"\n--- Exemplo {i} ---")
        print(f"Sequência de acessos: {seq}")
        print(f"Quadros disponíveis: {frames}")
        faults_fifo, writes_fifo = fifo(seq, frames)
        faults_lru, writes_lru = lru(seq, frames)
        print(f"FIFO => Page Faults: {faults_fifo}, Disk Writes: {writes_fifo}")
        print(f"LRU  => Page Faults: {faults_lru}, Disk Writes: {writes_lru}")