import com.xenomachina.argparser.ArgParser

class DnsServer(parser: ArgParser) {
    val port by parser.storing("" +
            "-p", "--port",
        help="port number")
}

fun main(args: Array<String>) {
    ArgParser(args).parseInto(::DnsServer).run {
        print("DNS Server started, listening at port ${this.port}")
    }
}