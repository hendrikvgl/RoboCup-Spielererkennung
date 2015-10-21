#ifndef _DEBUG_MAKRO_H
#define _DEBUG_MAKRO_H

//The Compiling DEBUG_LEVEL
// This should be defined in any CMAKE over a Flag, but if not, it's set to the current max level 4
#ifndef DEBUG_COMPILATION_LEVEL
    #define DEBUG_COMPILATION_LEVEL 7
    #define REDEFINED_LEVEL
#endif
#if DEBUG_COMPILATION_LEVEL == -1
    #define NODBG
#endif
//Current debuglevel given via console variable.
static const unsigned short DEBUG_EXECUTION_LEVEL = (getenv("DEBUG_LEVEL") != NULL) ?
                    *(getenv("DEBUG_LEVEL")) - '0' : DEBUG_COMPILATION_LEVEL;
//Const variable, is debug enabled
const static bool debug_enabled = (getenv("DEBUG") != NULL) && getenv("DEBUG")[0] == '1';

#ifdef __clang__
//Introduce an enum to customize the debug level
namespace Debug {
    enum Debug_Level{ERROR = 0, WARN = 1, IMPORTANT = 2, INFO = 3, EXPENSIVE = 4, NEW_FEATURE = 5};
}
//Directly use the namespaced enum values, so they can be accessed more comfortably, but keeping them in the correct namespace
using Debug::Debug_Level::ERROR;
using Debug::Debug_Level::WARN;
using Debug::Debug_Level::IMPORTANT;
using Debug::Debug_Level::INFO;
using Debug::Debug_Level::EXPENSIVE;
using Debug::Debug_Level::NEW_FEATURE;
#endif
#ifdef __GNUC__
#ifndef __clang__
    //The gcc can't handle this enum and direct using, so define the debug levels as macro
    #define ERROR 0
    #define WARN 1
    #define IMPORTANT 2
    #define INFO 3
    #define EXPENSIVE 4
    #define NEW_FEATURE 5
#endif
#endif

#define DO_WHILE_FALSE(...) do{__VA_ARGS__ ;}while(false)

#if defined NDEBUG || defined NPRINT_DEBUG
#define L_DEBUG(...) ;
#define L_LEVELED_DEBUG(...) ;
#define P_DEBUG(...) ;
#else
#define L_DEBUG(...) DO_WHILE_FALSE(__VA_ARGS__)
#define L_LEVELED_DEBUG(...) LEVELED_DEBUG(__VA_ARGS__)
#define P_DEBUG(...) DO_WHILE_FALSE(std::cout<< __VA_ARGS__ <<std::endl)
#endif

// This wrapper macro is used to appear as one argument when multiple arguments could be given as as ... parameter
#define WRAP(...) __VA_ARGS__
#define LP_DEBUG(LEVEL, ...) IF_DEBUG(LEVEL, WRAP(std::cout<< __VA_ARGS__ <<std::endl))
#ifndef LEVELED_DEBUG
    #define LEVELED_DEBUG(LEVEL, ...) IF_DEBUG(LEVEL, WRAP(__VA_ARGS__))
#endif // !defined LEVELED_DEBUG

// Define two Debug expressions by default
#define STANDART_IF_DEBUG_EXPRESSION(LEVEL) debug_enabled && DEBUG_EXECUTION_LEVEL >= LEVEL
#define VISION_IF_DEBUG_EXPRESSION(LEVEL) debug_enabled && DEBUG_EXECUTION_LEVEL >= LEVEL && m_debug_frame_nr == 0 && debug_vision
// Toggling between any DEBUGLEVEL or really no DEBUG from the Macros
// NODBG really takes out every Debug implemented over these macros
#ifdef NODBG
    #define DEBUG_SHAPES(LEVEL, ...) ;
    #define IF_DEBUG(LEVEL, EXPRESSIONS) ;
    #define IF_DEBUG_WITH_EXPRESSION(LEVEL, DEBUG_EXPRESION, EXPRESSION) ;

    #define DEBUG(LEVEL,KEY,VALUE) ;
    #define DEBUG_VAR_NAME(LEVEL,VAR,KEY,VALUE) ;

    #define DEBUG_LOG(LEVEL,MESSAGE) ;
    #define DEBUG_LOG_VAR_NAME(LEVEL, VAR, MESSAGE) ;

    #define DEBUG_TIMER(LEVEL, SCOPE) ;
    #define DEBUG_TIMER_VAR_NAME(LEVEL,VAR, SCOPE) ;
#else
    // Remember, IF_DEBUG is overridden by the vision, change there as well
    //Extend IF_DEBUG so it can be used with a given expression to check
    #define IF_DEBUG(LEVEL, EXPRESSION) IF_DEBUG_WITH_EXPRESSION(LEVEL, STANDART_IF_DEBUG_EXPRESSION(LEVEL), WRAP(EXPRESSION))
    #define IF_DEBUG_WITH_EXPRESSION(LEVEL, DEBUG_EXPRESSION, EXPRESSION) DEBUGLEVEL##LEVEL(if(DEBUG_EXPRESSION) {EXPRESSION;})
    //DEBUG_SHAPES
    #define DEBUG_SHAPES(LEVEL, ...) IF_DEBUG(LEVEL, m_debug_shapes.push_back(std::move(__VA_ARGS__)))
    //DEBUG Key-Value pair für die TreeView
    #define DEBUG(LEVEL,KEY,VALUE) DEBUG_VAR_NAME(LEVEL, m_debug, KEY, VALUE)
    #define DEBUG_VAR_NAME(LEVEL, VAR, KEY, VALUE) IF_DEBUG(LEVEL,VAR(KEY) = VALUE)
    //DEBUG_LOG ausgabe in der Konsole
    #define DEBUG_LOG(LEVEL,MESSAGE) DEBUG_LOG_VAR_NAME(LEVEL, m_debug, MESSAGE)
    #define DEBUG_LOG_VAR_NAME(LEVEL, VAR, MESSAGE) IF_DEBUG(LEVEL,VAR<<MESSAGE)
    //Der Debug-Timer muss ohne IF_DEBUG kommen
    #define DEBUG_TIMER(LEVEL, SCOPE) DEBUG_TIMER_VAR_NAME(LEVEL, m_debug, SCOPE)
    #define DEBUG_TIMER_VAR_NAME(LEVEL, VAR, SCOPE) Debug::Timer timer(VAR, SCOPE)
#endif


//Vision specific debug options will be declares at the end of this file due to conflicts because of other debug includes


// This is a information function to log current debuglevel
#define PRINT_DEBUG_INFO L_DEBUG(print_debug_information(__FILE__));
#include <iostream>
#define MACRCOMIN(X,Y) (X < Y ? X : Y)
inline void print_debug_information(std::string file)
{
    #ifndef NODBG
        std::cout<<"This file, "<<file<<" was compiled with Debuglevel "<<DEBUG_COMPILATION_LEVEL
                        <<" and is executet with Debuglevel "<< DEBUG_EXECUTION_LEVEL
            << ". This means all Debug declared higher than " << MACRCOMIN(DEBUG_COMPILATION_LEVEL,
                DEBUG_EXECUTION_LEVEL) << " won't be send to the Debughost." << std::endl;
    #else
        std::cout<<"This file, "<<file<<" was compiled with no Debug" << std::endl;
    #endif
    #ifdef _ROBOTVISION_HPP
        #define ENV(D) ((getenv(#D) != NULL) ? (getenv(#D)) : "")
        std::cout<<"Bekannte Variablen:" <<std::endl << "DEBUG: " << ENV(DEBUG)<< ", VISION_DEBUG: "
                << ENV(VISION_DEBUG) <<", VISION_DEBUG_FRAME_SKIP: " << ENV(VISION_DEBUG_FRAME_SKIP)
                << " DEBUG_LEVEL: " << ENV(DEBUG_LEVEL) << std::endl;
        #undef ENV
        #ifdef REDEFINED_LEVEL
            std::cout<< "No DEBUG_LEVEL was set, using default maximum debug level" <<std::endl;
        #endif
    #endif
}
#undef MACRCOMIN



//Giving the option to reach the DEBUG_SHAPES marco with only one parameter, to avoid trouble with commas
#define DEBUG_SHAPES7(EXPRESSION) DEBUG_SHAPES(7,EXPRESSION)
#define DEBUG_SHAPES6(EXPRESSION) DEBUG_SHAPES(6,EXPRESSION)
#define DEBUG_SHAPES5(EXPRESSION) DEBUG_SHAPES(5,EXPRESSION)
#define DEBUG_SHAPES4(EXPRESSION) DEBUG_SHAPES(4,EXPRESSION)
#define DEBUG_SHAPES3(EXPRESSION) DEBUG_SHAPES(3,EXPRESSION)
#define DEBUG_SHAPES2(EXPRESSION) DEBUG_SHAPES(2,EXPRESSION)
#define DEBUG_SHAPES1(EXPRESSION) DEBUG_SHAPES(1,EXPRESSION)
#define DEBUG_SHAPES0(EXPRESSION) DEBUG_SHAPES(0,EXPRESSION)

//Now Defining the different DEBUG_COMPILATION_LEVEL
#if DEBUG_COMPILATION_LEVEL >= 7
    #define DEBUGLEVEL7(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL7(EXPRESSION) ;
#endif
#if DEBUG_COMPILATION_LEVEL >= 6
    #define DEBUGLEVEL6(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL6(EXPRESSION) ;
#endif
#if DEBUG_COMPILATION_LEVEL >= 5
    #define DEBUGLEVEL5(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL5(EXPRESSION) ;
#endif
#if DEBUG_COMPILATION_LEVEL >= 4
    #define DEBUGLEVEL4(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL4(EXPRESSION) ;
#endif
#if DEBUG_COMPILATION_LEVEL >= 3
    #define DEBUGLEVEL3(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL3(EXPRESSION) ;
#endif
#if DEBUG_COMPILATION_LEVEL >= 2
    #define DEBUGLEVEL2(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL2(EXPRESSION) ;
#endif
#if DEBUG_COMPILATION_LEVEL >= 1
    #define DEBUGLEVEL1(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL1(EXPRESSION) ;
#endif
#if DEBUG_COMPILATION_LEVEL >= 0
    #define DEBUGLEVEL0(...) DO_WHILE_FALSE(__VA_ARGS__)
#else
    #define DEBUGLEVEL0(EXPRESSION) ;
#endif

#define DEBUGLEVELERROR(...) DEBUGLEVEL0(WRAP(__VA_ARGS__))
#define DEBUGLEVELWARN(...) DEBUGLEVEL1(WRAP(__VA_ARGS__))
#define DEBUGLEVELIMPORTANT(...) DEBUGLEVEL2(WRAP(__VA_ARGS__))
#define DEBUGLEVELINFO(...) DEBUGLEVEL3(WRAP(__VA_ARGS__))
#define DEBUGLEVELEXPENSIVE(...) DEBUGLEVEL4(WRAP(__VA_ARGS__))
#define DEBUGLEVELNEW_FEATURE(...) DEBUGLEVEL5(WRAP(__VA_ARGS__))

#endif //_DEBUG_MAKRO_H

#ifdef NEED_TIMER
    #ifndef SIMPLE_TIMER_DEFINED
    #define SIMPLE_TIMER_DEFINED
    #include <boost/date_time/posix_time/posix_time.hpp>
    namespace Debug {
    /**
     * A basic timer to determine block execution times
     */
    class TimerBase {
    protected:
        bool print;
        std::string name;
        boost::posix_time::ptime start;
        inline TimerBase(const std::string& name, bool print)
        : print(print), name(name) {
            start = boost::posix_time::microsec_clock::local_time();
        }

    public:
        inline TimerBase(const std::string& name)
        : print(true), name(name) {
            start = boost::posix_time::microsec_clock::local_time();
        }

        const boost::posix_time::ptime& get_start() const {
            return start;
        }

        inline float current_time() const {
            return (boost::posix_time::microsec_clock::local_time() - start).total_microseconds() * 0.001;
        }

        inline ~TimerBase() {
            if(print) {
                float ms = current_time();
                std::cout<< name << " benötigte " << ms << "ms"<<std::endl;
            }
        }
    };
    }
    #endif //SIMPLE_TIMER_DEFINED
#endif // NEED_TIMER

#ifndef VISION_DEBUG_SPECIALISATION_DEFINED
    //Vision spezifische Debug Optionen
    #ifdef CHANGE_IF_DEBUG_FOR_ROBOTVISION
        #ifndef NODBG
            #undef IF_DEBUG
            //Redefining IF_DEBUG to respect some vision specific debug options
            // Remember, IF_DEBUG is overridden by the vision, look at the original
            #define IF_DEBUG(LEVEL,EXPRESSION) IF_DEBUG_WITH_EXPRESSION(LEVEL, VISION_IF_DEBUG_EXPRESSION(LEVEL), EXPRESSION)
        #endif
        namespace Vision{
            static const bool debug_vision = getenv("VISION_DEBUG") != NULL && getenv("VISION_DEBUG")[0] == '1';
        }
    #define VISION_DEBUG_SPECIALISATION_DEFINED
    #endif //CHANGE_IF_DEBUG_FOR_ROBOTVISION
#endif //VISION_DEBUG_SPECIALISATION_DEFINED

