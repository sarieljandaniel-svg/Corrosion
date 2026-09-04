"""Inspection Manager tab."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import ttk

from ui.components import (
    badge,
    body_label,
    labeled_entry,
    meta_label,
    mono_font,
    newsprint_button,
    newsprint_card,
    page_header,
    configure_tree_style,
)
from ui.theme import ThemeTokens


def render_inspection(app, parent, tokens: ThemeTokens) -> None:
    configure_tree_style(tokens)
    parent.grid_columnconfigure(0, weight=2)
    parent.grid_columnconfigure(1, weight=1)

    page_header(parent, tokens, "Operations", "Inspection manager").grid(
        row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8)
    )

    left = ctk.CTkFrame(parent, fg_color="transparent")
    left.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
    right = ctk.CTkFrame(parent, fg_color="transparent")
    right.grid(row=1, column=1, sticky="nsew")

    # Target card
    target_card = newsprint_card(left, tokens)
    target_card.pack(fill="x", pady=(0, 12))
    sec = ctk.CTkFrame(target_card, fg_color="transparent")
    sec.pack(fill="x", padx=16, pady=14)
    meta_label(sec, tokens, "Target").pack(anchor="w")
    btn_row = ctk.CTkFrame(sec, fg_color="transparent")
    btn_row.pack(anchor="w", pady=(10, 0))
    app._crack_btn = newsprint_button(
        btn_row,
        tokens,
        "Crack detection",
        command=lambda: app.set_inspection("Crack"),
        variant="primary" if app.selected_inspection.get() == "Crack" else "secondary",
    )
    app._crack_btn.pack(side="left", padx=(0, 8))
    app._corrosion_btn = newsprint_button(
        btn_row,
        tokens,
        "Corrosion detection",
        command=lambda: app.set_inspection("Corrosion"),
        variant="primary" if app.selected_inspection.get() == "Corrosion" else "secondary",
    )
    app._corrosion_btn.pack(side="left")

    app.sub_options_frame = ctk.CTkFrame(target_card, fg_color="transparent")
    app.sub_options_frame.pack(fill="x", padx=16, pady=(0, 14))
    app._render_inspection_suboptions(tokens)

    cal = ctk.CTkFrame(target_card, fg_color="transparent")
    cal.pack(fill="x", padx=16, pady=(0, 14))
    ctk.CTkFrame(target_card, height=1, fg_color=tokens.border, corner_radius=0).pack(fill="x")
    cal_row = ctk.CTkFrame(cal, fg_color="transparent")
    cal_row.pack(fill="x", pady=14)
    w1, _ = labeled_entry(cal_row, tokens, "GSD (mm/px)", app.gsd_value, width=120)
    w1.pack(side="left", padx=(0, 16))
    w2, _ = labeled_entry(cal_row, tokens, "Frame stride", app.frame_stride_value, width=80)
    w2.pack(side="left", padx=(0, 16))
    w3, _ = labeled_entry(cal_row, tokens, "Inference width", app.inference_width_value, width=120)
    w3.pack(side="left")

    # Media hub
    media_card = newsprint_card(left, tokens)
    media_card.pack(fill="both", expand=True)
    inner = ctk.CTkFrame(media_card, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=16, pady=14)
    meta_label(inner, tokens, "Media hub").pack(anchor="w")
    body_label(inner, tokens, "MP4 queue", mono=True).pack(anchor="w", pady=(4, 10))

    actions = ctk.CTkFrame(inner, fg_color="transparent")
    actions.pack(fill="x", pady=(0, 10))
    newsprint_button(actions, tokens, "Add MP4…", command=app.upload_video).pack(side="left", padx=(0, 8))
    newsprint_button(actions, tokens, "Remove", command=app.remove_selected_video, variant="secondary").pack(
        side="left", padx=(0, 8)
    )
    newsprint_button(actions, tokens, "Open folder", command=app.open_selected_video_folder, variant="secondary").pack(
        side="left"
    )

    app.selected_video_lbl = body_label(inner, tokens, app._selected_video_label_text(), mono=True)
    app.selected_video_lbl.pack(anchor="w", pady=(0, 8))

    list_frame = ctk.CTkFrame(inner, fg_color="transparent")
    list_frame.pack(fill="both", expand=True)
    app.video_list = ttk.Treeview(list_frame, columns=["path"], show="headings", style="Newsprint.Treeview", height=5)
    app.video_list.heading("path", text="UPLOADED VIDEOS (DOUBLE-CLICK TO SELECT)")
    app.video_list.column("path", width=500, anchor="w")
    vsb = ttk.Scrollbar(list_frame, orient="vertical", command=app.video_list.yview)
    app.video_list.configure(yscrollcommand=vsb.set)
    app.video_list.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    list_frame.grid_rowconfigure(0, weight=1)
    list_frame.grid_columnconfigure(0, weight=1)
    app.video_list.bind("<Double-1>", lambda _e: app.select_video_from_list())
    app.video_list.bind("<<TreeviewSelect>>", lambda _e: app.select_video_from_list(update_only=True))

    run_row = ctk.CTkFrame(inner, fg_color="transparent")
    run_row.pack(fill="x", pady=(12, 0))
    newsprint_button(run_row, tokens, "Analyze selected video", command=app.run_engine_from_ui).pack(
        side="left", padx=(0, 8)
    )
    newsprint_button(run_row, tokens, "Stop", command=app.stop_engine_from_ui, variant="secondary").pack(side="left")
    app.status_lbl = body_label(inner, tokens, app.last_run_status.get(), mono=True)
    app.status_lbl.pack(anchor="w", pady=(10, 0))
    app._refresh_video_list()

    ctk.CTkFrame(inner, height=1, fg_color=tokens.border, corner_radius=0).pack(fill="x", pady=14)
    meta_label(inner, tokens, "IMX519 live feed").pack(anchor="w")
    body_label(
        inner,
        tokens,
        "PC listens first (same as ffplay -listen 1), then the Pi connects with rpicam-vid.",
        wraplength=520,
    ).pack(anchor="w", pady=(4, 10))

    live_row = ctk.CTkFrame(inner, fg_color="transparent")
    live_row.pack(fill="x", pady=(0, 8))
    w_ip, _ = labeled_entry(live_row, tokens, "Pi connects to (PC IP)", app.live_pc_ip, width=150)
    w_ip.pack(side="left", padx=(0, 12))
    w_port, _ = labeled_entry(live_row, tokens, "TCP port", app.live_listen_port, width=80)
    w_port.pack(side="left", padx=(0, 12))
    w_lw, _ = labeled_entry(live_row, tokens, "Width", app.live_width, width=80)
    w_lw.pack(side="left", padx=(0, 12))
    w_lh, _ = labeled_entry(live_row, tokens, "Height", app.live_height, width=80)
    w_lh.pack(side="left")

    ssh_row = ctk.CTkFrame(inner, fg_color="transparent")
    ssh_row.pack(fill="x", pady=(0, 8))
    w_pi, _ = labeled_entry(ssh_row, tokens, "Pi SSH host (optional)", app.pi_ssh_host, width=160)
    w_pi.pack(side="left", padx=(0, 12))
    w_user, _ = labeled_entry(ssh_row, tokens, "Pi SSH user", app.pi_ssh_user, width=100)
    w_user.pack(side="left", padx=(0, 12))
    ssh_wrap = ctk.CTkFrame(ssh_row, fg_color="transparent")
    ssh_wrap.pack(side="left", padx=(8, 0))
    meta_label(ssh_wrap, tokens, "Auto-start camera").pack(anchor="w", pady=(0, 4))
    ctk.CTkCheckBox(
        ssh_wrap,
        text="SSH rpicam-vid",
        variable=app.live_auto_ssh,
        font=mono_font(11),
        fg_color=tokens.button_primary_bg,
        hover_color=tokens.hover,
    ).pack(anchor="w")

    body_label(inner, tokens, "Command to run on the Raspberry Pi", mono=True).pack(anchor="w", pady=(4, 4))
    app.rpicam_cmd_box = ctk.CTkTextbox(
        inner,
        height=72,
        corner_radius=0,
        font=mono_font(11),
        wrap="word",
    )
    app.rpicam_cmd_box.pack(fill="x", pady=(0, 8))
    app._refresh_rpicam_command_box()
    if not getattr(app, "_rpicam_traces_bound", False):
        for var in (app.live_pc_ip, app.live_listen_port, app.live_width, app.live_height, app.live_bitrate):
            var.trace_add("write", lambda *_: app._refresh_rpicam_command_box())
        app._rpicam_traces_bound = True

    live_btns = ctk.CTkFrame(inner, fg_color="transparent")
    live_btns.pack(fill="x", pady=(0, 4))
    newsprint_button(live_btns, tokens, "Start live analysis", command=app.start_live_engine_from_ui).pack(
        side="left", padx=(0, 8)
    )
    newsprint_button(live_btns, tokens, "Stop live", command=app.stop_engine_from_ui, variant="secondary").pack(
        side="left", padx=(0, 8)
    )
    newsprint_button(live_btns, tokens, "Copy Pi command", command=app.copy_rpicam_command, variant="secondary").pack(
        side="left"
    )

    # Status panel + live view
    preview_card = newsprint_card(right, tokens)
    preview_card.pack(fill="both", expand=True, pady=(0, 12))
    pv = ctk.CTkFrame(preview_card, fg_color="transparent")
    pv.pack(fill="both", expand=True, padx=16, pady=14)
    meta_label(pv, tokens, "Annotated live view").pack(anchor="w")
    app.live_preview_lbl = ctk.CTkLabel(
        pv,
        text="Waiting for IMX519 stream…",
        text_color=tokens.muted,
        font=mono_font(12),
        anchor="center",
        justify="center",
        width=420,
        height=236,
    )
    app.live_preview_lbl.pack(fill="both", expand=True, pady=(10, 0))

    status_card = newsprint_card(right, tokens, inverted=True)
    status_card.pack(fill="x")
    si = ctk.CTkFrame(status_card, fg_color="transparent")
    si.pack(fill="x", padx=16, pady=16)
    meta_label(si, tokens, "Engine status", inverted=True).pack(anchor="w")
    badge_row = ctk.CTkFrame(si, fg_color="transparent")
    badge_row.pack(anchor="w", pady=(10, 0))
    app._engine_badge = badge(badge_row, tokens, app.last_run_status.get().lower(), tone="inverted")
    app._engine_badge.pack(side="left")
    if app.selected_inspection.get() == "Corrosion":
        badge(badge_row, tokens, "Corrosion", tone="accent").pack(side="left", padx=(8, 0))
    app._engine_status_lbl = ctk.CTkLabel(
        si,
        text=app.last_run_status.get(),
        text_color=tokens.inverted_fg,
        font=mono_font(12),
        anchor="w",
        justify="left",
        wraplength=240,
    )
    app._engine_status_lbl.pack(anchor="w", pady=(14, 0))
