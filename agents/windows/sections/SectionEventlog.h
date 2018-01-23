// +------------------------------------------------------------------+
// |             ____ _               _        __  __ _  __           |
// |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
// |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
// |           | |___| | | |  __/ (__|   <    | |  | | . \            |
// |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
// |                                                                  |
// | Copyright Mathias Kettner 2017             mk@mathias-kettner.de |
// +------------------------------------------------------------------+
//
// This file is part of Check_MK.
// The official homepage is at http://mathias-kettner.de/check_mk.
//
// check_mk is free software;  you can redistribute it and/or modify it
// under the  terms of the  GNU General Public License  as published by
// the Free Software Foundation in version 2.  check_mk is  distributed
// in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
// out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
// PARTICULAR PURPOSE. See the  GNU General Public License for more de-
// ails.  You should have  received  a copy of the  GNU  General Public
// License along with GNU Make; see the file  COPYING.  If  not,  write
// to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
// Boston, MA 02110-1301 USA.

#ifndef SectionEventlog_h
#define SectionEventlog_h

#include "Configurable.h"
#include "EventLog.h"
#include "Section.h"

class WinApiAdaptor;

// Configuration entries from [logwatch] for individual logfiles
struct eventlog_config_entry {
    eventlog_config_entry(int level, int hide_context, const char *name,
                          bool vista_api)
        : name(name)
        , level(level)
        , hide_context(hide_context)
        , vista_api(vista_api) {}

    std::string name;
    int level;
    int hide_context;
    bool vista_api;
};

template <>
eventlog_config_entry from_string<eventlog_config_entry>(
    const WinApiAdaptor &winapi, const std::string &value);

std::ostream &operator<<(std::ostream &out, const eventlog_config_entry &val);

// Our memory of what event logs we know and up to
// which record entry we have seen its messages so
// far.
struct eventlog_file_state {
    eventlog_file_state(const char *name)
        : name(name), newly_discovered(true) {}
    std::string name;
    uint64_t record_no;
    bool newly_discovered;
};

struct eventlog_hint_t {
    eventlog_hint_t(const std::string &name_, uint64_t record_no_)
        : name(name_), record_no(record_no_) {}
    std::string name;
    uint64_t record_no;
};

using eventlog_config_t = std::vector<eventlog_config_entry>;
using eventlog_state_t = std::vector<eventlog_file_state>;
using eventlog_hints_t = std::vector<eventlog_hint_t>;

class EventlogConfigurable
    : public ListConfigurable<eventlog_config_t,
                              BlockMode::Nop<eventlog_config_t>,
                              AddMode::PriorityAppend<eventlog_config_t>> {
    using SuperT =
        ListConfigurable<eventlog_config_t, BlockMode::Nop<eventlog_config_t>,
                         AddMode::PriorityAppend<eventlog_config_t>>;

public:
    EventlogConfigurable(Configuration &config, const char *section,
                         const char *key, const WinApiAdaptor &winapi)
        : SuperT(config, section, key, winapi) {}

    virtual void feed(const std::string &var,
                      const std::string &value) override {
        eventlog_config_entry entry =
            from_string<eventlog_config_entry>(_winapi, value);
        const auto tokens = tokenize(var, " ");

        if (tokens.size() < 2) {
            std::cerr << "Invalid eventlog logname entry: '" << var << "'"
                      << std::endl;
        }

        entry.name = join(std::next(tokens.cbegin()), tokens.cend(), " ");
        entry.vista_api = (tokens[0] == "logname");
        add(entry);
    }
};

eventlog_hint_t parseStateLine(const std::string &line);

class SectionEventlog : public Section {
public:
    SectionEventlog(Configuration &config, Logger *logger,
                    const WinApiAdaptor &winapi);
    virtual ~SectionEventlog();

    virtual void postprocessConfig() override;

protected:
    virtual bool produceOutputInner(std::ostream &out) override;

private:
    uint64_t outputEventlog(std::ostream &out, const char *logname,
                            uint64_t previouslyReadId, int level,
                            int hideContext);
    void registerEventlog(const char *logname);
    bool find_eventlogs(std::ostream &out);
    void loadEventlogOffsets(const std::string &statefile);
    void saveEventlogOffsets(const std::string &statefile);

    Configurable<bool> _send_initial;
    Configurable<bool> _vista_api;
    EventlogConfigurable _config;
    eventlog_hints_t _hints;
    eventlog_state_t _state;
    bool _records_loaded = false;
    bool _first_run = true;
};

#endif  // SectionEventlog_h
