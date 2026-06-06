
function fcc --description "Launch free-claude-code proxy + claude from the local repo"

    set -l FCC_DIR  "$HOME/tools/free-claude-code"
    set -l FCC_PORT 8082
    set -l FCC_LOG  "$HOME/.cache/fcc-server.log"
    set -l HEALTH   "http://127.0.0.1:$FCC_PORT/health"

    if not test -d "$FCC_DIR"
        echo "fcc: repo not found at $FCC_DIR" >&2
        return 1
    end

    if test (count $argv) -ge 1; and test "$argv[1]" = server
        echo "==> Starting fcc-server (foreground)…"
        uv run --project "$FCC_DIR" fcc-server
        return
    end

    set -l server_pid 0

    echo "==> Starting fcc-server in background (log: $FCC_LOG)…"
    mkdir -p (dirname "$FCC_LOG")
    nohup uv run --project "$FCC_DIR" fcc-server >$FCC_LOG 2>&1 &
    set server_pid $last_pid
    disown $server_pid

    echo -n "==> Waiting for server to become healthy"
    set -l attempts 0
    while not curl -sf "$HEALTH" >/dev/null 2>&1
        set attempts (math $attempts + 1)
        if test $attempts -ge 30
            echo ""
            echo "fcc: server did not become healthy after 15 s." >&2
            echo "     Check the log: $FCC_LOG" >&2
            kill $server_pid 2>/dev/null
            return 1
        end
        echo -n "."
        sleep 0.5
    end
    echo " ready ✓"

    echo "==> Launching fcc-claude…"
    uv run --project "$FCC_DIR" fcc-claude $argv
    set -l claude_exit $status

    echo ""
    echo "==> Stopping fcc-server (PID $server_pid)…"
    kill $server_pid 2>/dev/null
    # give it up to 3 s to exit cleanly
    set -l waited 0
    while kill -0 $server_pid 2>/dev/null; and test $waited -lt 6
        sleep 0.5
        set waited (math $waited + 1)
    end
    if kill -0 $server_pid 2>/dev/null
        kill -9 $server_pid 2>/dev/null
    end
    echo "==> fcc-server stopped."

    return $claude_exit
end
