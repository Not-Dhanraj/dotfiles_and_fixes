-- Spring Boot language server support, layered on top of the lang.java extra.
-- Adds application.properties/yml completion, @RequestMapping navigation, and
-- bean references. It hooks its bundles into the existing jdtls automatically.
return {
  {
    "JavaHello/spring-boot.nvim",
    ft = { "java", "yaml", "jproperties" },
    dependencies = { "mfussenegger/nvim-jdtls" },
  },
}
