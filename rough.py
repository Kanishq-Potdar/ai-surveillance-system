def run_camera(video_source, camera_id):
    cap   = cv2.VideoCapture(video_source)
    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results  = model(frame)
        annotated = results[0].plot()

        for box in results[0].boxes:
            label      = results[0].names[int(box.cls)]
            confidence = float(box.conf)

            if label in WATCH_FOR and confidence > 0.5:
                now = datetime.now()

                # Log to database with cooldown
                last_time = last_logged.get(label + camera_id)  # separate cooldown per camera
                if last_time is None or (now - last_time).seconds >= COOLDOWN_SECONDS:
                    log_event(label, confidence)
                    last_logged[label + camera_id] = now

                # Sound alert with its own cooldown (10 seconds so it's not annoying)
                # Sound + email alert with cooldown
                last_alert_time = last_alerted.get(label + camera_id)  # separate cooldown per camera
                if label in HIGH_PRIORITY:
                    if last_alert_time is None or (now - last_alert_time).seconds >= 10:
                        # Sound alert
                        play_alert()
                        last_alerted[label + camera_id] = now
                        print(f"🔔 ALERT: {label} detected!")

                        # Email alert in background thread (so video doesn't freeze)
                        # Only email every 60 seconds to avoid inbox spam
                        last_email_time = last_alerted.get(label + camera_id + "_email")
                        if last_email_time is None or (now - last_email_time).seconds >= 60:
                            threading.Thread(
                                target=send_email_alert,
                                args=(label, confidence, camera_id),
                                daemon=True
                            ).start()
                            last_alerted[label + camera_id + "_email" ] = now

        cv2.imshow(f"AI Surveillance - Camera {camera_id}", annotated)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break